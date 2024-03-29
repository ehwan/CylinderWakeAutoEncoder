#! /usr/bin/python3

import os

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import torch

import autoencoder
import stepper as stp

encoder = autoencoder.AutoEncoder()
encoder.load_state_dict( torch.load( 'autoencoder.pt' ) )
encoder.train( False )
stepper = stp.LatentStepper()
stepper.load_state_dict( torch.load( 'stepper.pt' ) )
stepper.train( False )

# current state ( velx, vely )
state = torch.zeros( size=(1,2,256,512), dtype=torch.float32 )
latent = encoder.encoder( state )
cylinder_mask = torch.ones( (1, 1, 256, 512), dtype=torch.float32 )
dx = 10.0 / 511.0
for y in range(256):
  for x in range(512):
    fx = x*dx
    fy = y*dx
    fx = fx - 2.5
    fy = fy - 2.5
    if fx*fx + fy*fy < 0.5*0.5:
      state[0, 0, y, x] = 0.0
      state[0, 1, y, x] = 0.0
      cylinder_mask[0, 0, y, x] = 0.0
    else:
      state[0, 0, y, x] = 1.0
      state[0, 1, y, x] = 0.0

def step( re ):
  global state
  global latent
  latent = encoder.encoder( state )
  next_latent = stepper.step( latent, re )
  next_state = encoder.decoder( next_latent )
  state = next_state*cylinder_mask
  latent = next_latent

def plot( i ):
  Vx = state[0][0].detach().numpy()
  Vy = state[0][1].detach().numpy()
  Xs = np.linspace(0, 10, 512)
  Ys = np.linspace(0, 5, 256)
  Xs, Ys = np.meshgrid(Xs, Ys)
  Vx = Vx[::4,::4]
  Vy = Vy[::4,::4]
  Xs = Xs[::4,::4]
  Ys = Ys[::4,::4]
  fig = plt.figure(1, figsize=(10, 5))
  norm = mpl.colors.Normalize( vmin=0, vmax=1.5 )
  plt.quiver( Xs, Ys, Vx, Vy, np.sqrt(Vx**2 + Vy**2), scale=4, scale_units='xy', units='xy', norm=norm )
  fig.gca().add_patch( plt.Circle( (2.5,2.5), 0.5, color='black' ) )
  plt.colorbar()
  # plt.show()
  plt.savefig( 'plots/plot{:04d}.png'.format(i) )
  plt.clf()
  plt.cla()

os.mkdir( 'plots' )
for i in range(400):
  print( i )
  plot(i)
  step(5.0)