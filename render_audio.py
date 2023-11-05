# author: samtenka
# change: 2023-11-05
# create: 2023-10-31
# descrp: render audio clip as a nice .png of wave, emphasizing high freq
# to use: 

from pydub import AudioSegment
from pydub.playback import play
import numpy as np

import matplotlib.pyplot as plt
import matplotlib

a = AudioSegment.from_file("sound1.wav")
a = AudioSegment.from_file("Studied.mp3")
FR = a.frame_rate
y = np.array(a.get_array_of_samples()).astype(np.float32) / 2.**15
y = y[55000:255000]
y = y[::2]
t = np.arange(len(y)).astype(np.float32) / FR
print()
print(y)
print(max(y))
print(min(y))
#play(audio1)

RNG = (0.95, 0.65, 0.05)
BLU = (0.05, 0.55, 0.85)
GRE = (0.55, 0.55, 0.55)

axd = plt.figure(figsize=(7*2,1.5*2), layout='constrained').subplot_mosaic(
        '''
        AAAAAAAAA
        BBBCCCDDD
        BBBCCCDDD
        BBBCCCDDD
        BBBCCCDDD
        '''
        )
for c in 'ABCD':
    axd[c].xaxis.set_tick_params(labelbottom=False)
    axd[c].xaxis.set_ticks([])
    axd[c].yaxis.set_ticks([])
    axd[c].yaxis.set_tick_params(labelbottom=False)
    axd[c].spines['bottom'].set_visible(False)
    axd[c].spines['left'  ].set_visible(False)
    axd[c].spines['right' ].set_visible(False)
    axd[c].spines['top'   ].set_visible(False)

BOX = False

axd['A'].plot(t, y, c=RNG, lw=0.8)

dn = 2205

for ax,n in [
        (axd['B'], FR*0),
        (axd['C'], FR*1),
        (axd['D'], FR*2),
        ]:
    tt, yy = t[n:n+dn], y[n:n+dn]

    xm,xM = n/FR, float(n+dn)/FR
    ym,yM = -1,+1

    axd['A'].plot([xm,xm], [ym,yM], c=GRE, lw=0.8)
    axd['A'].plot([xM,xM], [ym,yM], c=GRE, lw=0.8)
    axd['A'].plot([xm,xM], [ym,ym], c=GRE, lw=0.8)
    axd['A'].plot([xm,xM], [yM,yM], c=GRE, lw=0.8)

    ax.plot([xm,xm], [ym,yM], c=GRE, lw=0.8)
    ax.plot([xM,xM], [ym,yM], c=GRE, lw=0.8)
    ax.plot([xm,xM], [ym,ym], c=GRE, lw=0.8)
    ax.plot([xm,xM], [yM,yM], c=GRE, lw=0.8)

    fig = plt.gcf()
    fig.canvas.draw()
    transFigure = fig.transFigure.inverted()

    if BOX:
        for aa in [xm,xM]:
            for bb in [ym,yM]:
                coord1 = transFigure.transform(axd['A'].transData.transform([aa,bb]))
                coord2 = transFigure.transform(ax      .transData.transform([aa,bb]))
                line = matplotlib.lines.Line2D((coord1[0],coord2[0]),(coord1[1],coord2[1]),
                                               transform=fig.transFigure, c=GRE, lw=0.8)
                fig.lines.append(line)

    diff = yy[1:]-yy[:-1]
    diff /= max(abs(max(diff)), abs(min(diff)))
    #diff += 0.5
    #diff /= max(abs(max(diff)), abs(min(diff)))
    diff = np.clip(diff, -1.,+1.)
    diff = .5*(diff + np.sign(diff))
    #switch = np.clip(np.abs(np.sign(diff[1:])-np.sign(diff[:-1])), 0., .5)
    #switch = .5*(switch + np.sign(switch ))
    #ax.scatter(tt[2:], switch, color=BLU, lw=0.8, marker='.', s=1)
    ax.scatter(tt[1:], diff, color=GRE, lw=0.8, marker='.', s=1)
    ax.plot(tt, yy, c=RNG, lw=1.6)



plt.savefig('yo.png')


