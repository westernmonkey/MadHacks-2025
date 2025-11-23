import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class LiveBandwidthPredictor(nn.Module):
    def __init__(self, max_total_bandwidth=100.0):
        super().__init__()
        
        # --- BANDWIDTH CONSTRAINT ---
        self.max_total_bandwidth = max_total_bandwidth  # e.g., 100 Mbps total
        
        # --- INDEPENDENT PREDICTORS (One per packet type) ---
        self.high_predictor = nn.Linear(1, 1)
        self.neutral_predictor = nn.Linear(1, 1)
        self.low_predictor = nn.Linear(1, 1)
        
        # Initialize: 2.0 Mbps per packet + 5.0 Mbps base
        for predictor in [self.high_predictor, self.neutral_predictor, self.low_predictor]:
            nn.init.constant_(predictor.weight, 2.0)
            nn.init.constant_(predictor.bias, 5.0)
        
        # --- OPTIMIZER ---
        self.optimizer = optim.SGD(self.parameters(), lr=0.000001, momentum=0.9)
        
    @property
    def slice_weights(self):
        """Returns the learned cost (Mbps per packet) for each slice type"""
        return {
            'HIGH': self.high_predictor.weight.item(),
            'NEUTRAL': self.neutral_predictor.weight.item(),
            'LOW': self.low_predictor.weight.item(),
        }

    def forward(self, high_count, neutral_count, low_count, apply_constraint=True):
        """
        Each packet type predicts its own bandwidth independently
        Then apply constraint to keep total under max_total_bandwidth
        """
        high_bw = self.high_predictor(high_count)
        neutral_bw = self.neutral_predictor(neutral_count)
        low_bw = self.low_predictor(low_count)
        
        if apply_constraint:
            # Calculate total predicted bandwidth
            total_bw = high_bw + neutral_bw + low_bw
            
            # If over limit, scale down proportionally
            if total_bw > self.max_total_bandwidth:
                scale_factor = self.max_total_bandwidth / total_bw
                high_bw = high_bw * scale_factor
                neutral_bw = neutral_bw * scale_factor
                low_bw = low_bw * scale_factor
        
        return high_bw, neutral_bw, low_bw

    def _prepare_input(self, packets_dict):
        """Convert dict to three separate tensors"""
        high = torch.tensor([[packets_dict[0]]], dtype=torch.float32)
        neutral = torch.tensor([[packets_dict[1]]], dtype=torch.float32)
        low = torch.tensor([[packets_dict[2]]], dtype=torch.float32)
        return high, neutral, low

    def predict(self, packets_dict):
        """Make a prediction based on packet counts"""
        high, neutral, low = self._prepare_input(packets_dict)
        
        with torch.no_grad():
            high_bw, neutral_bw, low_bw = self.forward(high, neutral, low, apply_constraint=True)
            
            result = {
                'HIGH': round(max(0, high_bw.item()), 2),
                'NEUTRAL': round(max(0, neutral_bw.item()), 2),
                'LOW': round(max(0, low_bw.item()), 2),
            }
            
            # Verify constraint
            total = sum(result.values())
            assert total <= self.max_total_bandwidth + 0.01, f"Constraint violated! Total: {total}"
            
            return result

    def train(self, packets_dict, actual_bandwidths_dict):
        """
        Train each predictor independently
        Note: We train on UNCONSTRAINED predictions, but predict WITH constraints
        This allows the model to learn true costs, then scale at inference time
        """
        # 1. Prepare Inputs
        high, neutral, low = self._prepare_input(packets_dict)
        
        # 2. Prepare Targets
        y_high = torch.tensor([[actual_bandwidths_dict.get('HIGH', 0.0)]], dtype=torch.float32)
        y_neutral = torch.tensor([[actual_bandwidths_dict.get('NEUTRAL', 0.0)]], dtype=torch.float32)
        y_low = torch.tensor([[actual_bandwidths_dict.get('LOW', 0.0)]], dtype=torch.float32)
        
        # 3. Zero Gradients
        self.optimizer.zero_grad()
        
        # 4. Forward Pass (WITHOUT constraint during training)
        pred_high, pred_neutral, pred_low = self.forward(high, neutral, low, apply_constraint=False)
        
        # 5. Calculate Individual Losses
        loss_high = F.mse_loss(pred_high, y_high)
        loss_neutral = F.mse_loss(pred_neutral, y_neutral)
        loss_low = F.mse_loss(pred_low, y_low)
        
        # Total loss
        loss = loss_high + loss_neutral + loss_low
        
        # 6. Backward Pass
        loss.backward()
        
        # 7. Update Weights
        self.optimizer.step()
        
        # Return predictions and errors (using constrained predictions for logging)
        with torch.no_grad():
            pred_high_c, pred_neutral_c, pred_low_c = self.forward(high, neutral, low, apply_constraint=True)
            predictions = [pred_high_c.item(), pred_neutral_c.item(), pred_low_c.item()]
            errors = [
                pred_high_c.item() - y_high.item(),
                pred_neutral_c.item() - y_neutral.item(),
                pred_low_c.item() - y_low.item(),
            ]
        
        return predictions, errors


