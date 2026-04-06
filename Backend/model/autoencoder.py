# Backend/model/autoencoder.py

import torch
import torch.nn as nn

class Autoencoder(nn.Module):
    """
    A simple autoencoder for transaction anomaly detection.
    
    Architecture:
    Input (8 features)
        → Encoder Layer 1 (8 → 16)
        → Encoder Layer 2 (16 → 8)
        → Bottleneck      (8 → 4)
        → Decoder Layer 1 (4 → 8)
        → Decoder Layer 2 (8 → 16)
        → Output          (16 → 8)
    
    The bottleneck forces the model to compress the transaction
    into 4 numbers — learning only the most important patterns.
    """

    def __init__(self, input_dim: int = 8):
        super(Autoencoder, self).__init__()

        # ── Encoder ───────────────────────────────────────────────────────────
        # Compresses input down to bottleneck
        # ReLU is the activation function — it adds non-linearity
        # without it the network would just be a linear transformation
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 4),
            nn.ReLU(),
        )

        # ── Decoder ───────────────────────────────────────────────────────────
        # Reconstructs input from bottleneck
        # Sigmoid at the end squashes output between 0 and 1
        # which matches our normalized input range
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass — runs input through encoder then decoder.
        This is called automatically when you do model(x).
        """
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """
        Returns just the compressed bottleneck representation.
        Not used for anomaly detection but useful for debugging.
        """
        return self.encoder(x)


if __name__ == "__main__":
    # ── Quick sanity check ────────────────────────────────────────────────────
    # Creates a model and runs a fake transaction through it
    # to make sure the shapes are all correct

    model = Autoencoder(input_dim=8)
    print("── Model Architecture ───────────────────────────────")
    print(model)

    # fake batch of 4 transactions with 8 features each
    fake_input = torch.randn(4, 8)
    print(f"\n── Input shape:  {fake_input.shape}")

    output = model(fake_input)
    print(f"── Output shape: {output.shape}")

    bottleneck = model.encode(fake_input)
    print(f"── Bottleneck shape: {bottleneck.shape}")

    # input and output should have the same shape
    assert fake_input.shape == output.shape, "Input and output shapes don't match!"
    print("\n✓ Shape check passed — autoencoder is working correctly")

    # count total parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"✓ Total parameters: {total_params}")