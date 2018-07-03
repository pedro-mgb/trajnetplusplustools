
from contextlib import contextmanager
import matplotlib.pyplot as plt
import os
import pysparkling
import trajnettools


@contextmanager
def show(fig_file=None, **kwargs):
    fig, ax = plt.subplots(**kwargs)

    yield ax

    fig.set_tight_layout(True)
    if fig_file:
        os.makedirs(os.path.dirname(fig_file), exist_ok=True)
        fig.savefig(fig_file, dpi=300)
    fig.show()
    plt.close(fig)


def predict(input_files):
    sc = pysparkling.Context()
    paths = (sc
             .wholeTextFiles(input_files)
             .mapValues(trajnettools.readers.trajnet)
             .cache())
    kalman_predictions = (paths
                          .mapValues(lambda paths: paths[0])
                          .mapValues(trajnettools.kalman.predict))
    lstm_predictor = trajnettools.lstm.VanillaPredictor.load('output/vanilla_lstm.pkl')
    lstm_predictions = (paths
                        .mapValues(lambda paths: paths[0])
                        .mapValues(lstm_predictor))
    olstm_predictor = trajnettools.lstm.VanillaPredictor.load('output/olstm.pkl')
    olstm_predictions = paths.mapValues(olstm_predictor)

    paths = (paths
             .leftOuterJoin(kalman_predictions)
             .leftOuterJoin(lstm_predictions)
             .leftOuterJoin(olstm_predictions))
    for scene, (((gt, kf), lstm), olstm) in paths.toLocalIterator():
        output_file = (scene
                       .replace('/train/', '/train_plots/')
                       .replace('/test/', '/test_plots/')
                       .replace('.txt', '.png'))
        with show(output_file) as ax:
            # KF prediction
            ax.plot([gt[0][8].x] + [r.x for r in kf],
                    [gt[0][8].y] + [r.y for r in kf], color='orange', label='KF')
            ax.plot([kf[-1].x], [kf[-1].y], color='orange', marker='x', linestyle='None')

            # LSTM prediction
            ax.plot([gt[0][8].x] + [r.x for r in lstm],
                    [gt[0][8].y] + [r.y for r in lstm], color='blue', label='LSTM')
            ax.plot([lstm[-1].x], [lstm[-1].y], color='blue', marker='x', linestyle='None')

            # OLSTM prediction
            ax.plot([gt[0][8].x] + [r.x for r in olstm],
                    [gt[0][8].y] + [r.y for r in olstm], color='green', label='O-LSTM')
            ax.plot([olstm[-1].x], [olstm[-1].y], color='green', marker='x', linestyle='None')

            # ground truths
            for i_gt, g in enumerate(gt):
                xs = [r.x for r in g]
                ys = [r.y for r in g]

                # markers
                label_start = None
                label_end = None
                if i_gt == 0:
                    label_start = 'start'
                    label_end = 'end'
                ax.plot(xs[0:1], ys[0:1], color='black', marker='o', label=label_start, linestyle='None')
                ax.plot(xs[-1:], ys[-1:], color='black', marker='x', label=label_end, linestyle='None')

                # ground truth lines
                ls = 'dotted' if i_gt > 0 else 'solid'
                label = None
                if i_gt == 0:
                    label = 'primary'
                if i_gt == 1:
                    label = 'others'
                ax.plot(xs, ys, color='black', linestyle=ls, label=label)

            # frame
            ax.legend()
            ax.set_xlabel('x [m]')
            ax.set_ylabel('y [m]')


if __name__ == '__main__':
    predict('output/test/biwi_eth/?.txt')
    # predict('output/train/biwi_hotel/?.txt')
