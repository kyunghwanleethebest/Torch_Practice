import argparse

import torch
import torch.nn as nn
import torch.optim as optim

from dnn_model import ImageClassifier
from trainer import Trainer
from utils import load_mnist

def define_argparser():
    p = argparse.ArgumentParser()

    p.add_argument('--model_fn', required=True)
    p.add_argument('--gpu_id', type=int, default=0 if torch.cuda.is_available() else -1)
    p.add_argument('--train_ratio', type=float, default=.8)
    p.add_argument('--batch_size', type=int, default=64)
    p.add_argument('--n_epochs', type=int, default=20)
    p.add_argument('--verbose', type=int, default=2)

    config = p.parse_args()

    return config

def main(config):
    device = torch.device('cpu') if config.gpu_id < 0 else torch.device('cuda:%d' % config.gpu_id)

    x, y = load_mnist(is_train=True)

    # Tensor => Chunk of 1-d vectors
    x = x.view(x.size(0), -1)

    train_cnt = int(x.size(0) * config.train_ratio)
    valid_cnt = x.size(0) - train_cnt

    # Shuffle
    indices = torch.randperm(x.size(0))
    x = torch.index_select(
        x,
        dim=0,
        index=indices
    ).to(device).split([train_cnt, valid_cnt], dim=0)

    y = torch.index_select(
        y,
        dim=0,
        index=indices
    ).to(device).split([train_cnt, valid_cnt], dim=0)

    print("Train:", x[0].shape, y[0].shape)
    print("Valid:", x[1].shape, y[1].shape)

    model = ImageClassifier(28**2, 10).to(device)
    optimizer = optim.Adam(model.parameters())
    crit = nn.NLLLoss

    # Save best model weights
    torch.save({
        'model': trainer.model.state_dict(),
        'config': config,

    }, config.model_fn)

    if __name__ == '__main__':
        config = define_argparser()
        main(config)

