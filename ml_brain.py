import torch
import torch.nn as nn
import torch.optim as optim


class LiveBandwidthPredictor(nn.Module):
   def __init__(self):
       super().__init__()
      
       # --- MODEL PARAMETERS (PyTorch Tensors) ---
       # We model: Bandwidth = (w1 * packets) + (w2 * packets^2) + bias
       # We initialize w1 to 1.0 to start with a reasonable guess
       self.w1 = nn.Parameter(torch.tensor(1.0, dtype=torch.float32))
       self.w2 = nn.Parameter(torch.tensor(0.0, dtype=torch.float32))
       self.bias = nn.Parameter(torch.tensor(0.0, dtype=torch.float32))
      
       # --- OPTIMIZER ---
       # SGD with Momentum is standard for converging quickly without oscillation
       self.optimizer = optim.SGD(self.parameters(), lr=0.000001, momentum=0.9)
      
   @property
   def weight(self):
       """Helper to keep ai_controller.py happy (it expects .weight)"""
       return self.w1.item()


   def forward(self, x):
       """The Prediction Formula"""
       # Linear term + Quadratic term + Bias
       return (self.w1 * x) + (self.w2 * (x**2)) + self.bias


   def predict(self, packets):
       """Make a prediction without updating gradients"""
       with torch.no_grad():
           x = torch.tensor(float(packets))
           prediction = self.forward(x)
           return max(0, round(prediction.item(), 2))


   def train(self, packets, actual_bandwidth):
       """
       The PyTorch Training Step
       """
       # 1. Prepare Data
       x = torch.tensor(float(packets))
       y_true = torch.tensor(float(actual_bandwidth))
      
       # 2. Zero Gradients (Reset from last step)
       self.optimizer.zero_grad()
      
       # 3. Forward Pass (Make Prediction)
       y_pred = self.forward(x)
      
       # 4. Calculate Loss (Mean Squared Error)
       loss = (y_pred - y_true) ** 2
      
       # 5. Backward Pass (Calculate Gradients automatically)
       loss.backward()
      
       # 6. Update Weights
       self.optimizer.step()
      
       # Return values for the controller
       prediction_val = y_pred.item()
       error = prediction_val - y_true.item()
      
       return prediction_val, error
