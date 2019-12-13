import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

__all__ = ['KimNet', 'ConvNet', 'init_weights']

"""
Neural network models are defined here
"""
class KimNet(nn.Module):
    """
    An implementation of the histone-mark based NN model from Kim: EP-DNN (2016)
    Network is MLP, with a input-600-500-400-output architecture.
    """
    def __init__(self, bins=20, marks=3, nb_cls=5):
        super(KimNet, self).__init__()
        self.bins = bins
        self.marks = marks
        self.model = nn.Sequential(
            nn.Linear(bins*marks, 600),
            nn.Softplus(),
            nn.Linear(600, 500),
            nn.Softplus(),
            nn.Linear(500, 400),
            nn.Softplus(),
            nn.Dropout(0.5),
            nn.Linear(400, nb_cls),
            nn.Softmax(dim=1)
        )

    def forward(self, histone_forward, histone_reverse=None):
        o = self.model(histone_forward.view((-1, self.bins*self.marks)))
        if histone_reverse is not None:
            o2 = self.model(histone_reverse.view((-1, self.bins*self.marks)))
            o = torch.add(o, o2)
            o = torch.div(o, 2)
        return torch.log(o)


class ConvNet(nn.Module):
    def __init__(self, marks=3, nb_cls=5, use_leakyrelu=False):
        assert nb_cls > 1, 'output layer size must be at least 2.'
        super(ConvNet, self).__init__()

        self.layer_one = nn.Sequential(
            #in channels, out channels, kernel size
            nn.Conv1d(marks, 32, 7, padding=3), 
            nn.BatchNorm1d(32),
            nn.LeakyReLU() if use_leakyrelu else nn.ReLU(),
        )
        self.layer_two = nn.Sequential(
            nn.Conv1d(32, 32, 3, padding=1),
            nn.BatchNorm1d(32),
            nn.LeakyReLU() if use_leakyrelu else nn.ReLU(),
            nn.MaxPool1d(2, stride=2)
        )
        self.layer_three = nn.Sequential(
            nn.Conv1d(32, 64, 3, padding=1),
            nn.BatchNorm1d(64),
            nn.LeakyReLU() if use_leakyrelu else nn.ReLU(),
        )
        self.layer_four = nn.Sequential(
            nn.Conv1d(64, 64, 3, padding=1),
            nn.BatchNorm1d(64),
            nn.LeakyReLU() if use_leakyrelu else nn.ReLU(),
            nn.MaxPool1d(2, stride=2)
        )

        self.final_layer = nn.Sequential( 
            nn.AdaptiveAvgPool1d(1),
            nn.Conv1d(64, nb_cls, 1),
            nn.Softmax(dim=1)
        )
        
    def forward(self, histone_forward, histone_reverse=None):
        def _forward_prop(x):
            '''Forward an input through all layers and return 
            an output
            '''
            o = self.layer_one(x)
            o = self.layer_two(o)
            o = self.layer_three(o)
            o = self.layer_four(o)
            o = self.final_layer(o)
            return o
        
        # forward histone data.
        o = _forward_prop(histone_forward)
        # reverse histone data.
        if histone_reverse is not None:
            o2 = _forward_prop(histone_reverse)
            o = torch.add(o, o2)
            o = torch.div(o, 2)

        return torch.squeeze(torch.log(o))


def init_weights(m):
    if isinstance(m, nn.Conv1d):
        nn.init.kaiming_uniform_(m.weight.data, nonlinearity='relu')
        nn.init.zeros_(m.bias.data)
    elif isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight.data, nonlinearity='relu')
        nn.init.zeros_(m.bias.data)






