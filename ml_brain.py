import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F # Used for loss calculation

class LiveBandwidthPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        
        # --- MODEL PARAMETERS (The core of the prediction engine) ---
        # Input features: 3 types of packets [HIGH, NEUTRAL, LOW]
        # Output features: 3 predicted bandwidths [BW_HIGH, BW_NEUTRAL, BW_LOW]
        self.linear = nn.Linear(in_features=3, out_features=3)
        
        # Initialize weights (w) and bias (b)
        # We start guessing 2.0 Mbps per packet for all types
        nn.init.constant_(self.linear.weight, 2.0) 
        nn.init.constant_(self.linear.bias, 5.0)   # Base overhead (5 Mbps)
        
        # --- OPTIMIZER ---
        self.optimizer = optim.SGD(self.parameters(), lr=0.000001, momentum=0.9)
        
    @property
    def slice_weights(self):
        """Helper to get the current learned cost (Mbps per packet) for each slice."""
        # Returns the learned cost (Mbps) for the 3 slice types
        return self.linear.weight.data.mean(dim=1).tolist() 

    def forward(self, x):
        """Input x is a Tensor of shape (1, 3) -> Output is shape (1, 3)"""
        return self.linear(x)

    def _prepare_input(self, packets_dict):
        """Maps dict keys to the fixed tensor index order: [HIGH, NEUTRAL, LOW]"""
        return torch.tensor([
            packets_dict.get('HIGH', 0.0),
            packets_dict.get('NEUTRAL', 0.0),
            packets_dict.get('LOW', 0.0),
        ], dtype=torch.float32).unsqueeze(0) # Shape (1, 3)

    def predict(self, packets_dict):
        """Make a prediction based on the dictionary of packet counts"""
        x = self._prepare_input(packets_dict)
        
        with torch.no_grad():
            prediction = self.forward(x)
            
            # Returns a dictionary of 3 predicted bandwidths
            predicted_bws = prediction.squeeze().tolist()
            return {
                'HIGH': round(max(0, predicted_bws[0]), 2),
                'NEUTRAL': round(max(0, predicted_bws[1]), 2),
                'LOW': round(max(0, predicted_bws[2]), 2),
            }

    def train(self, packets_dict, actual_bandwidths_dict):
        """
        The PyTorch Training Step: updates weights based on actual usage for all 3 outputs.
        """
        # 1. Prepare Inputs (Packets)
        x = self._prepare_input(packets_dict)
        
        # 2. Prepare Targets (Actual Bandwidth Used)
        y_targets = [
            actual_bandwidths_dict.get('HIGH', 0.0),
            actual_bandwidths_dict.get('NEUTRAL', 0.0),
            actual_bandwidths_dict.get('LOW', 0.0),
        ]
        y_true = torch.tensor([y_targets], dtype=torch.float32) # Shape (1, 3)
        
        # 3. Zero Gradients
        self.optimizer.zero_grad()
        
        # 4. Forward Pass (Make 3 Predictions)
        y_pred = self.forward(x)
        
        # 5. Calculate Loss (Mean Squared Error across all 3 outputs)
        loss = F.mse_loss(y_pred, y_true)
        
        # 6. Backward Pass (Calculate Gradients automatically)
        loss.backward()
        
        # 7. Update Weights
        self.optimizer.step()
        
        # Calculate individual errors for logging
        errors = (y_pred - y_true).squeeze().tolist()
        
        return y_pred.squeeze().tolist(), errors