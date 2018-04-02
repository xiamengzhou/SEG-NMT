from __future__ import division
from tmmt.nmt import *
from tmmt.layer import *
from pprint import pprint
from tmmt.setup import setup
from tmmt.data_iterator import TextIterator, prepare_data, prepare_cross
from termcolor import colored as clr
from tmmt.translate_gpu import go
import pickle as pkl

import itertools
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str, default='fren')
args = parser.parse_args()

model_options = setup(args.m)
if model_options['remote']:
    try:
        monitor = Monitor(model_options['address'], model_options['port'])
        print('create a remote monitor')
    except Exception:
        print('error to create a monitor')
        monitor = None
else:
    monitor = None

pprint(model_options)

# add random seed
model_options['rng']  = numpy.random.RandomState(seed=19920206)
model_options['trng'] = RandomStreams(model_options['rng'].randint(0, 2**32-1))
model_options['n_words_src'] = model_options['voc_sizes'][0]
model_options['n_words'] = model_options['voc_sizes'][1]

# the number of TM
model_options['n_inputs'] = len(model_options['datasets'])

# load dictionaries and invert them
worddicts   = [None] * len(model_options['dictionaries'])
worddicts_r = [None] * len(model_options['dictionaries'])
for ii, dd in enumerate(model_options['dictionaries']):
    with open(dd, 'rb') as f:
        worddicts[ii] = pkl.load(f)
    worddicts_r[ii] = dict()
    for kk, vv in worddicts[ii].iteritems():
        worddicts_r[ii][vv] = kk


funcs, tp = build_networks(model_options)

if model_options['see_pretrain']:
    tparams, tparams_xy0 = tp
else:
    tparams = tp
# print 'save the compiled functions/tparams for temperal usage'


print('Loading data')
train = TextIterator(model_options['datasets'], model_options['dictionaries'],
                     [0 for _ in range(model_options['n_inputs'])],
                     batch_size=model_options['batch_size'], maxlen=model_options['maxlen'])
valid = TextIterator(model_options['valid_datasets'], model_options['dictionaries'],
                     [0 for _ in range(model_options['n_inputs'])],
                     batch_size=model_options['batch_size'], maxlen=500)


print(clr('-------------------------------------------- Main-Loop -------------------------------------------------', 'yellow'))

# ------------------ initlization --------------- #
best_p       = None
bad_counter  = 0
uidx         = 0
estop        = False
history_errs = []
max_epochs   = 100
finish_after = 10000000

lrate        = model_options['lrate']
saveFreq     = model_options['saveFreq']
sampleFreq   = model_options['sampleFreq']
validFreq    = model_options['validFreq']
bleuFreq     = model_options['bleuFreq']
saveto       = model_options['saveto']
overwrite    = model_options['overwrite']

if monitor:
    import datetime
    timestamp = datetime.datetime.now().strftime("%m-%d_%H:%M")
    monitor.start_experiment('train.{}.{}'.format(timestamp, model_options['saveto']))

# ----------------------------------------------- #

# reload history
if model_options['reload_'] and os.path.exists(model_options['saveto']):
    rmodel = numpy.load(model_options['saveto'])
    history_errs = list(rmodel['history_errs'])
    if 'uidx' in rmodel:
        uidx = rmodel['uidx']


# idx back to sequences
def idx2seq(x, ii, pp=None):
    seq = []
    for kk, vv in enumerate(x):
        if vv == 0:
            break
        if vv in worddicts_r[ii]:
            word = worddicts_r[ii][vv]

            if pp is None:
                if vv > model_options['voc_sizes'][ii]:
                    seq.append(clr(word, 'green'))
                else:
                    seq.append(word)
            else:
                if pp[kk] == 0:
                    seq.append(clr(word, 'red'))
                elif (pp[kk] > 0) and (pp[kk] <= 0.25):
                    seq.append(clr(word, 'yellow'))
                elif (pp[kk] > 0.25) and (pp[kk] <= 0.5):
                    seq.append(clr(word, 'green'))
                elif (pp[kk] > 0.5) and (pp[kk] <= 0.75):
                    seq.append(clr(word, 'cyan'))
                else:
                    seq.append(clr(word, 'blue'))

        else:
            seq.append(clr('UNK', 'white'))
    return ' '.join(seq)


@Timeit
def execute(inps, lrate, info):
    eidx, uidx = info
    rets = funcs['cost'](*inps)
    cost, g2 = rets[0], rets[1]
    print('Epoch {}: update {},'.format(eidx, uidx),)
    print('cost {:.2f}, g-norm {:.1f}'.format(float(cost), float(g2)),)

    # check for bad numbers, usually we remove non-finite elements
    # and continue training - but not done here
    if numpy.isnan(g2):
        print('NaN error again!!!')
        raise Exception('Gradient NaN detected')

    if numpy.isnan(cost):
        raise Exception('Cost NaN detected')

    if numpy.isinf(cost):
        raise Exception('Cost Inf detected')

    funcs['update'](lrate)

    return cost


@Timeit
def validate(funcs, options, iterator, verbose=False):
    probs = []

    n_done = 0
    for k, inputs in enumerate(iterator):
        xs, xs_mask = zip(*[prepare_data(inputs[k], 500, options['voc_sizes'][k])
                            for k in range(0, options['n_inputs'], 2)])
        ys, ys_mask = zip(*[prepare_data(inputs[k], 500, model_options['voc_sizes'][k])
                            for k in range(1, model_options['n_inputs'], 2)])

        tys, tys_mask = zip(*[prepare_cross(inputs[1], inputs[k], ys[0].shape[0])
                              for k in range(3, model_options['n_inputs'], 2)])
        tys = list(tys)
        lens = 0
        for k in range(len(tys)):
            tys[k] += lens
            lens += ys[k + 1].shape[0]

        inps = []
        for k in range(len(xs)):
            inps += [xs[k], xs_mask[k], ys[k], ys_mask[k]]
        for k in range(len(tys)):
            inps += [tys[k], tys_mask[k]]

        if options['use_coverage']:
            if not options.get('nn_coverage', False):
                lens = 0
                for k in range(1, len(ys)):
                    lens += ys[k].shape[0]
                inps += [numpy.zeros((ys[1].shape[1], lens), dtype='float32')]  # initial coverage
            else:
                raise NotImplementedError

        pprobs = funcs['valid'](*inps)
        for pp in pprobs:
            probs.append(pp)

        if verbose:
            print >>sys.stderr, '%d samples computed' % (n_done)

    return numpy.array(probs)


@Timeit
def savemodel(udix=0):
    print('Saving the best model...',)
    if best_p is not None:
        params = best_p
    else:
        params = unzip(tparams)

    numpy.savez(saveto, history_errs=history_errs, uidx=uidx, **params)
    pkl.dump(model_options, open('%s.pkl' % saveto, 'wb'))
    print('Done')

    # save with uidx
    if not overwrite:
        print('Saving the model at iteration {}...'.format(uidx),)
        saveto_uidx = '{}.iter{}.npz'.format(
            os.path.splitext(saveto)[0], uidx)
        numpy.savez(saveto_uidx, history_errs=history_errs,
                    uidx=uidx, **unzip(tparams))
        print('Done')


class BLEU(threading.Thread):
    def __init__(self, options, steps, start_steps=0,
                max_steps=finish_after, sleep=1000):
        super(BLEU, self).__init__()
        self.options  = options
        self.steps    = steps
        self.maxsteps = max_steps
        self.startsteps = start_steps
        self.sleep    = sleep

    def run(self):
        print('[test] Hello, I am Thread: %s.' % (threading.currentThread().getName()))
        options = self.options
        go(options['saveto'],
           options['dictionaries'][0],
           options['dictionaries'][1],
           options['trans_from'],
           options['tm_source'],
           options['tm_target'],
           options['trans_to'],
           options['beamsize'],
           options['normalize'],
           options['d_maxlen'],
           steps=self.steps,
           max_steps=self.maxsteps,
           start_steps=self.startsteps,
           sleep=self.sleep)


if uidx == 0:
    print('save an initial model...')
    savemodel(0)

if not model_options['disable_bleu']:
    print('start a BLUE tester...')
    bleuer = BLEU(model_options, bleuFreq, start_steps=(uidx//bleuFreq) * bleuFreq)
    bleuer.start()

print('start the main loop...')
for eidx in range(max_epochs):
    n_samples = 0

    for k, inputs in enumerate(train):
        uidx += 1

        _skip =  model_options.get('skip', 0)
        if uidx < _skip:
            continue

        # save the best model so far, in addition, save the latest model
        # into a separate file with the iteration number for external eval
        if numpy.mod(uidx, saveFreq) == 0:
            savemodel(uidx)

        # validate model on validation set and early stop if necessary
        if numpy.mod(uidx, validFreq) == 0:
            # use_noise.set_value(0.)
            valid_errs = validate(funcs, model_options, valid, False)
            valid_err  = float(valid_errs.mean())
            history_errs.append(valid_err)

            if numpy.isnan(valid_err):
                print('NaN detected')
                sys.exit(-1)

            print('Valid ', valid_err)
            if monitor:
                try:
                    monitor.push({'valid': float(str(valid_err))}, step=int(uidx))
                except Exception:
                    print(e)

        xs, xs_mask = zip(*[prepare_data(inputs[k], 500, model_options['voc_sizes'][k])
                            for k in range(0, model_options['n_inputs'], 2)])
        ys, ys_mask = zip(*[prepare_data(inputs[k], 500, model_options['voc_sizes'][k])
                            for k in range(1, model_options['n_inputs'], 2)])

        tys, tys_mask = zip(*[prepare_cross(inputs[1], inputs[k], ys[0].shape[0])
                            for k in range(3, model_options['n_inputs'], 2)])
        tys = list(tys)

        # additional process --> add an off-set...
        lens = 0
        for k in range(len(tys)):
            tys[k] += lens
            lens += ys[k+1].shape[0]

        inps = []
        for k in range(len(xs)):
            inps += [xs[k], xs_mask[k], ys[k], ys_mask[k]]
        for k in range(len(tys)):
            inps += [tys[k], tys_mask[k]]

        if model_options['use_coverage']:
            if not model_options.get('nn_coverage', False):
                lens = 0
                for k in range(1, len(ys)):
                    lens += ys[k].shape[0]
                inps += [numpy.zeros((ys[1].shape[1], lens), dtype='float32')]  # initial coverage
            else:
                raise NotImplementedError

        try:
            execute(inps, lrate, [eidx, uidx])  # train one step.
        except Exception as  e:
            print(clr(e, 'red'))
            continue

        # generate some samples with the model and display them
        if numpy.mod(uidx, sampleFreq) == 0:
            for jj in range(numpy.minimum(5, xs[0].shape[1])):
                stochastic = True

                print('=============================')
                K = model_options['n_inputs']
                for k in range(2, K, 2):
                    print('Source-TM {}: {}'.format(k//2, idx2seq(inputs[k][jj], k)))
                    print('Target-TM {}: {}'.format(k//2, idx2seq(inputs[k + 1][jj], k + 1)))

                print('Source-CR: {}'.format(idx2seq(inputs[0][jj], 0)))
                print('Target-CR: {}'.format(idx2seq(inputs[1][jj], 1)))

                print('----------------------------------------------------------------------------')

                xss = [xs[k][:, jj][:, None] for k in range(1, K//2)]
                yss = [ys[k][:, jj][:, None] for k in range(1, K//2)]
                sample, sc, acts, gg = gen_sample_multi(tparams, funcs,
                                                        xs[0][:, jj][:, None],
                                                        xss, yss,
                                                        model_options,
                                                        rng=model_options['rng'],
                                                        m=0, k=model_options['beamsize'],
                                                        maxlen=200,
                                                        stochastic=model_options['stochastic'],
                                                        argmax=True)

                if model_options['stochastic']:
                    ss  = sample
                    act = acts
                    gg_ = gg
                else:
                    sc /= numpy.array([len(s) for s in sample]).astype('float32')
                    ss = sample[sc.argmin()]
                    act = acts[sc.argmin()]
                    gg_ = gg[sc.argmin()]

                _yss = list(itertools.chain.from_iterable([inputs[k] for k in range(3, K, 2)]))
                _ss = []
                for ii, si in enumerate(ss):
                    if si < model_options['voc_sizes'][1]:
                        _ss.append(si)
                    else:
                        offset = si - model_options['voc_sizes'][1]
                        if offset < len(_yss[jj]):
                            _ss.append(_yss[jj][offset])
                        else:
                            _ss.append(0)

                if model_options['see_pretrain']:
                    sample0, sc0  = gen_sample(tparams_xy0,
                                               funcs['init_xy0'],
                                               funcs['next_xy0'],
                                               xs[0][:, jj][:, None],
                                               model_options,
                                               rng=model_options['rng'],
                                               k=model_options['beamsize'],
                                               maxlen=200,
                                               stochastic=model_options['stochastic'],
                                               argmax=True)

                    if model_options['stochastic']:
                        ss0 = sample0
                    else:
                        sc0 /= numpy.array([len(s) for s in sample0]).astype('float32')
                        ss0  = sample0[sc0.argmin()]


                    # print 'Sample-CR {}: {}'.format(jj, idx2seq(_ss, 1))
                    print('NMT Model: {}'.format(idx2seq(ss0, 1)))

                print('Copy Prob: {}'.format(idx2seq(_ss, 1, act)))
                print('Copy Gate: {}'.format(idx2seq(_ss, 1, gg_)))

        # finish after this many updates
        if uidx >= finish_after:
            print('Finishing after %d iterations!' % uidx)
            estop = True
            break

    print('Seen %d samples' % n_samples)

    if estop:
        break

if best_p is not None:
    zipp(best_p, tparams)

valid_err = validate(funcs, model_options, valid).mean()
print('Valid ', valid_err)

bleuer.join()
params = copy.copy(best_p)
numpy.savez(saveto, zipped_params=best_p,
            history_errs=history_errs,
            uidx=uidx,
            **params)



