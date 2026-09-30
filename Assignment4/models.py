"""Pre-implemented models of sound event recognition."""

import torch

from config import SAMPLE_RATE, SNIPPET_DURATION


class WaveformModel(torch.nn.Module):
    """ Super simple model that operates directly on raw waveforms: 5 fully connected layers with tanh activations,
    followed by a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        input_length = int(SAMPLE_RATE * SNIPPET_DURATION)
        hidden_sizes = (1024, 512, 256, 128, 64)

        self.flatten = torch.nn.Flatten()

        sizes = [input_length, *hidden_sizes]
        self.hidden_layers = torch.nn.ModuleList([
            torch.nn.Linear(sizes[i], sizes[i + 1]) for i in range(len(hidden_sizes))
        ])
        self.activation = torch.nn.Tanh()

        self.classifier = torch.nn.Linear(hidden_sizes[-1], num_classes)

    def forward(
            self,
            waveform: torch.Tensor
    ) -> torch.Tensor:
        x = self.flatten(waveform)
        for layer in self.hidden_layers:
            x = self.activation(layer(x))
        return self.classifier(x)


class UninspiredModel(torch.nn.Module):
    """ More complex but still uninspired model that now operates on spectrograms: 3 convolutional layers with
    tanh activations, followed by 2 fully connected layers and a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        fc_sizes = (64, 128, 64)

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.Tanh()

        self.fc_layers = torch.nn.ModuleList([
            torch.nn.Linear(fc_sizes[i], fc_sizes[i + 1]) for i in range(len(fc_sizes) - 1)
        ])

        self.classifier = torch.nn.Linear(fc_sizes[-1], num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))
        x = x.mean(dim=(-2, -1))
        for fc in self.fc_layers:
            x = self.activation(fc(x))
        return self.classifier(x)


class InspiredModel(torch.nn.Module):
    """ The most complex model, operating on spectrograms: 3 convolutional layers with ReLU6 activations extract local
    time-frequency features, 2 stacked recurrent (GRU) layers integrate information over time, and a linear classifier
    returns logits. Its conv -> recurrent structure loosely mirrors the auditory system's hierarchy of local
    spectrotemporal filtering followed by temporal integration.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        rnn_hidden_size = 128

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.ReLU6()

        self.rnn = torch.nn.GRU(
            input_size=conv_channels[-1], hidden_size=rnn_hidden_size, num_layers=2, batch_first=True,
        )

        self.classifier = torch.nn.Linear(rnn_hidden_size, num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        """ Runs the model forward.

        Args:
            spectrogram: Tensor of shape (batch, 1, n_freq, n_time).

        Returns:
            Logits of shape (batch, num_classes).
        """
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))

        x = x.mean(dim=2).transpose(1, 2)

        _, hidden = self.rnn(x)
        last_hidden = hidden[-1]

        return self.classifier(last_hidden)

class BiologicalModel(torch.nn.Module):
    """ A biologically inspired CRNN modeling the auditory pathway.
    
    Motivated Mapping:
    - A1: Initial convolutional layer for basic spectrotemporal feature extraction.
    - LBelt & MBelt: Two parallel convolutional branches for specialized intermediate processing.
    - PBelt: Concatenation and convolution to integrate the parallel belt pathways.
    - A4: Final convolutional abstraction layer.
    - A5/STS: Bidirectional GRU to integrate temporal context over the sequence.
    
    Args: num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        
        # We use ReLU6 to model the biological constraint that 
        # neurons cannot fire negatively (lower bound 0) and have an absolute 
        # maximum firing rate capacity (upper bound 6).
        self.activation = torch.nn.ReLU6()

        # Downsamples the feature maps to reduce dimensionality and simulate pooling in the auditory cortex.
        # Early layer pools frequency and time.
        self.pool_both = torch.nn.MaxPool2d(kernel_size=(2,2))

        # Later layers pool only frequency (dimension 0), preserving time (dimension 1).
        self.pool_freq = torch.nn.MaxPool2d(kernel_size=(2,1))

        # Primary Auditory Cortex (A1)
        # Input channels: 1 (Mel-spectrogram). Output: 32
        self.conv_a1 = torch.nn.Conv2d(1, 32, kernel_size=3, padding=1)
        # size=3 simulates local lateral inhibition, alpha, beta, and k are hyperparameters that control the normalization effect.
        # These parameters alpha, beta and k are set to these values because these values are the established, historically proven hyperparameters originally derived empirically by Krizhevsky et al. (2012) in the AlexNet architecture.
        # The size parameter was adapted from 5 to 3 to scale with our network's more constrained channel capacity.
        self.norm_a1 = torch.nn.LocalResponseNorm(size=3, alpha=1e-4, beta=0.75, k=2.0)

        # Lateral Belt (LBelt) & Medial Belt (MBelt)
        # Two parallel branches, both receiving input from A1
        self.conv_lbelt = torch.nn.Conv2d(32, 32, kernel_size=3, padding=1)
        self.norm_lbelt = torch.nn.LocalResponseNorm(size=3, alpha=1e-4, beta=0.75, k=2.0)
        
        self.conv_mbelt = torch.nn.Conv2d(32, 32, kernel_size=3, padding=1)
        self.norm_mbelt = torch.nn.LocalResponseNorm(size=3, alpha=1e-4, beta=0.75, k=2.0)

        # Parabelt (PBelt)
        # Receives concatenated input from LBelt (32) and MBelt (32), so 64 channels
        self.conv_pbelt = torch.nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.norm_pbelt = torch.nn.LocalResponseNorm(size=5, alpha=1e-4, beta=0.75, k=2.0) # The size parameter is increased to 5 to allow for a broader normalization effect across the combined feature maps from both belt areas, reflecting the increased complexity and integration at this stage of auditory processing.

        # A4 Region. The output from this layer will be fed into the recurrent layer for temporal integration.
        # The output channels are increased to 128 to allow for richer feature representation before temporal integration.
        self.conv_a4 = torch.nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.norm_a4 = torch.nn.LocalResponseNorm(size=5, alpha=1e-4, beta=0.75, k=2.0)

        # A5 / Superior Temporal Sulcus (STS)
        # Recurrent layer for temporal integration. Bidirectional models context
        # from both past and future acoustic cues.
        rnn_hidden_size = 128 # The hidden size is set to 128 to balance model capacity and computational efficiency.
        self.rnn = torch.nn.GRU(
            input_size=128, 
            hidden_size=rnn_hidden_size, 
            num_layers=2, # Two layers allow the model to capture more complex temporal dependencies in the auditory signal.
            batch_first=True, # Ensures that the input and output tensors are of shape (batch, seq, feature), which is standard for sequence data.
            bidirectional=True # The bidirectional setting allows the GRU to capture context from both past and future time steps, which is important for understanding temporal patterns in auditory signals.
        )

        # Final Classifier
        # Input size is 256 because the GRU is bidirectional (128 * 2 = 256)
        self.classifier = torch.nn.Linear(rnn_hidden_size * 2, num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        """ Runs the model forward.

        Args:
            spectrogram: Tensor of shape (batch, 1, n_freq, n_time).

        Returns:
            Logits of shape (batch, num_classes).
        """
        # A1 Processing
        x_a1 = self.pool_both(self.activation(self.norm_a1(self.conv_a1(spectrogram))))

        # Parallel Belt Processing
        x_lbelt = self.pool_freq(self.activation(self.norm_lbelt(self.conv_lbelt(x_a1))))
        x_mbelt = self.pool_freq(self.activation(self.norm_mbelt(self.conv_mbelt(x_a1))))

        # PBelt Integration (Concatenate LBelt and MBelt along the channel dimension)
        x_merged = torch.cat([x_lbelt, x_mbelt], dim=1)
        x_pbelt = self.pool_freq(self.activation(self.norm_pbelt(self.conv_pbelt(x_merged))))

        # A4 Processing
        x_a4 = self.pool_freq(self.activation(self.norm_a4(self.conv_a4(x_pbelt))))

        # Transition from Convolutions to Recurrence
        # Average across the remaining frequency (tonotopic) bins, keeping the time dimension
        x_temporal = x_a4.mean(dim=2).transpose(1, 2)

        # A5/STS Temporal Integration
        _, hidden = self.rnn(x_temporal)
        
        # Extract the final hidden states from both forward and backward RNN passes
        last_hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)

        return self.classifier(last_hidden)
