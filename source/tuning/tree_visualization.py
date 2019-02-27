import os
import pickle
import numpy as np
import pandas as pd


def relative_deviation(obs, pred):
    return np.abs(obs-pred)/obs * 100


def path2latex_formula(estimator, features, sample):
    if len(sample.shape) > 1 and sample.shape[1] > 1:
        print('Subject one sample at a time.')
        return
    if len(sample.shape) == 1:
        sample = sample.reshape(1, -1)

    feature = estimator.tree_.feature
    threshold = estimator.tree_.threshold

    node_indicator = estimator.decision_path(sample)
    leave_id = estimator.apply(sample)

    node_index = node_indicator.indices[node_indicator.indptr[0]:
                                        node_indicator.indptr[1]]
    decisions = []
    for node_id in node_index:
        if leave_id[0] == node_id:
            continue

        if (sample[0, feature[node_id]] <= threshold[node_id]):
            threshold_sign = '$\\le$'
        else:
            threshold_sign = '$>$'

        decisions.append(
            '\\textit{{{0}}} {1} {2:.3f}'.format(
                features[feature[node_id]], threshold_sign, threshold[node_id]
            )
        )
    rule = ' $\\wedge$ '.join(decisions)
    return rule


def generate_path_table(estimator, data, target, output_path):
    X = data.values[:, :-1]
    y = data.values[:, -1]
    y_pred = estimator.predict(data.values[:, :-1])
    rds = relative_deviation(y, y_pred)
    with open(
            os.path.join(output_path, 'path_table_{}.tex'.format(target)),
            'w'
         ) as f:
        f.write('% Add to the document preamble: \\usepackage{array}\n')
        f.write('\\begin{table}[!htbp]\n')
        f.write('\t\\setlength{\\tabcolsep}{3pt}\n')
        f.write('\t\\begin{tabular}{ccccm{0.7\\textwidth}}\n')
        f.write('\t\t\\toprule\n')
        f.write('\t\tid & $T_g$ & $\\hat{T_g}$ & RD (\\%) & Tree branch\\\\\n')
        f.write('\t\t\\midrule\n')

        for i in range(len(data)):
            line = '{:02d} & {:.2f} & {:.2f} & {:.2f} & {}\\\\'.format(
                i, y[i], y_pred[i], rds[i],
                path2latex_formula(
                    estimator=estimator,
                    features=list(data),
                    sample=X[i]
                )
            )
            f.write('\t\t' + line + '\n')
            if i < len(data) - 1:
                f.write('\t\t\\hline\n')
        f.write('\t\t\\bottomrule\n')
        f.write('\t\\end{tabular}\n')
        f.write('\\end{table}\n')


def main(dataset_path, output_path, targets):
    for target, ftarget in targets.items():
        with open(
                '../../result/dt/default_dt_{}.model'.format(target), 'rb'
             ) as f:
            estimator = pickle.load(f)
        data = pd.read_csv('{}{}_test_rem.csv'.format(dataset_path, ftarget))
        generate_path_table(estimator, data, target, output_path)


dataset_path = '../../data/clean/oxides_'
output_path = '../../result/interpretation'
targets = {
    'tg': 'Tg',
    'nd300': 'ND300',
    'tl': 'Tliquidus'
}


if __name__ == '__main__':
    main(dataset_path, output_path, targets)
