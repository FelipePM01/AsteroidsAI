
import matplotlib.pyplot as plt
from IPython import display

plt.ioff()

def plot(scores, mean_scores):
    fig=plt.figure()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.savefig('plots/plot.png')
    plt.close(fig)
    plt.pause(.1)

def plot_time(time):
    fig=plt.figure()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Time')
    plt.plot(time)
    plt.ylim(ymin=0)
    plt.text(len(time)-1, time[-1], str(time[-1]))
    plt.savefig('plots/plot.png')
    plt.close(fig)
    plt.pause(.1)
