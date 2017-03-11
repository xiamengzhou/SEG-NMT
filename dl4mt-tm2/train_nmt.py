from __future__ import division
from nmt import *
from pprint import pprint
from setup import setup
from data_iterator import TextIterator, prepare_data, prepare_cross
from termcolor import colored as clr

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str, default='fren')
args = parser.parse_args()

model_options = setup(args.m)
pprint(model_options)

# add random seed
model_options['rng']  = numpy.random.RandomState(seed=19920206)
model_options['trng'] = RandomStreams(model_options['rng'].randint(0, 2**32-1))
model_options['n_words_src'] = model_options['voc_sizes'][0]
model_options['n_words'] = model_options['voc_sizes'][1]


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
tparams, tparams_xy0 = tp

# print 'save the compiled functions/tparams for temperal usage'


print 'Loading data'
train = TextIterator(model_options['datasets'], model_options['dictionaries'], [0, 0, 0, 0],
                     batch_size=model_options['batch_size'], maxlen=model_options['maxlen'])
valid = TextIterator(model_options['valid_datasets'], model_options['dictionaries'], [0, 0, 0, 0],
                     batch_size=model_options['batch_size'], maxlen=200)


print clr('-------------------------------------------- Main-Loop -------------------------------------------------',
          'yellow')

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
saveto       = model_options['saveto']
overwrite    = model_options['overwrite']

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


# compute-update
@Timeit
def execute(inps, lrate, info):
    eidx, uidx = info
    cost, g_cost = funcs['cost'](*inps)
    print 'Epoch ', eidx, 'Update ', uidx, 'Cost ', cost, 'G', g_cost,

    # check for bad numbers, usually we remove non-finite elements
    # and continue training - but not done here
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
    for k, (sx1, sy1, sx2, sy2) in enumerate(iterator):
        x1, x1_mask = prepare_data(sx1, 200, options['voc_sizes'][0])
        y1, y1_mask = prepare_data(sy1, 200, options['voc_sizes'][1])
        x2, x2_mask = prepare_data(sx2, 200, options['voc_sizes'][2])
        y2, y2_mask = prepare_data(sy2, 200, options['voc_sizes'][3])
        ty12, ty12_mask = prepare_cross(sy1, sy2, y1.shape[0])

        inps = [x1, x1_mask, y1, y1_mask,
                x2, x2_mask, y2, y2_mask,
                ty12, ty12_mask]
        if options['use_coverage']:
            inps += [numpy.zeros((y2.shape[1], y2.shape[0]), dtype='float32')]

        pprobs = funcs['valid'](*inps)
        for pp in pprobs:
            probs.append(pp)

        if verbose:
            print >>sys.stderr, '%d samples computed' % (n_done)

    return numpy.array(probs)


# start!!
for eidx in xrange(max_epochs):
    n_samples = 0

    for k, (sx1, sy1, sx2, sy2) in enumerate(train):
        uidx += 1

        x1, x1_mask = prepare_data(sx1, model_options['maxlen'], model_options['voc_sizes'][0])
        y1, y1_mask = prepare_data(sy1, model_options['maxlen'], model_options['voc_sizes'][1])
        x2, x2_mask = prepare_data(sx2, model_options['maxlen'], model_options['voc_sizes'][2])
        y2, y2_mask = prepare_data(sy2, model_options['maxlen'], model_options['voc_sizes'][3])
        ty12, ty12_mask = prepare_cross(sy1, sy2, y1.shape[0])

        # print 'x1:{}, x2:{}, y1:{}, y2:{}'.format(x1.shape, x2.shape, y1.shape, y2.shape)

        inps = [x1, x1_mask, y1, y1_mask,
                x2, x2_mask, y2, y2_mask,
                ty12, ty12_mask]
        if model_options['use_coverage']:
            inps += [numpy.zeros((y2.shape[1], y2.shape[0]), dtype='float32')]

        try:
            execute(inps, lrate, [eidx, uidx])  # train one step.

        except Exception, e:
            print clr(e, 'red')
            continue

        # save the best model so far, in addition, save the latest model
        # into a separate file with the iteration number for external eval
        if numpy.mod(uidx, saveFreq) == 0:
            print 'Saving the best model...',
            if best_p is not None:
                params = best_p
            else:
                params = unzip(tparams)

            numpy.savez(saveto, history_errs=history_errs, uidx=uidx, **params)
            pkl.dump(model_options, open('%s.pkl' % saveto, 'wb'))
            print 'Done'

            # save with uidx
            if not overwrite:
                print 'Saving the model at iteration {}...'.format(uidx),
                saveto_uidx = '{}.iter{}.npz'.format(
                    os.path.splitext(saveto)[0], uidx)
                numpy.savez(saveto_uidx, history_errs=history_errs,
                            uidx=uidx, **unzip(tparams))
                print 'Done'

        # generate some samples with the model and display them
        if numpy.mod(uidx, sampleFreq) == 0:
            for jj in xrange(numpy.minimum(5, x1.shape[1])):
                stochastic = True
                sample, sc, acts, gg = gen_sample_memory(tparams, funcs,
                                                         x1[:, jj][:, None],
                                                         x2[:, jj][:, None],
                                                         y2[:, jj][:, None],
                                                         model_options,
                                                         rng=model_options['rng'],
                                                         m=0, k=model_options['beamsize'],
                                                         maxlen=200,
                                                         stochastic=model_options['stochastic'],
                                                         argmax=True)

                sample0, sc0  = gen_sample(tparams_xy0,
                                           funcs['init_xy0'],
                                           funcs['next_xy0'],
                                           x1[:, jj][:, None],
                                           model_options,
                                           rng=model_options['rng'],
                                           k=model_options['beamsize'],
                                           maxlen=200,
                                           stochastic=model_options['stochastic'],
                                           argmax=True)

                print '============================='
                print 'Target-TM {}: {}'.format(jj, idx2seq(sy2[jj], 3))
                print 'Source-TM {}: {}'.format(jj, idx2seq(sx2[jj], 2))
                print 'Source-CR {}: {}'.format(jj, idx2seq(sx1[jj], 0))
                print 'Target-CR {}: {}'.format(jj, idx2seq(sy1[jj], 1))
                print '-----------------------------'

                if model_options['stochastic']:
                    ss  = sample
                    act = acts
                    gg_ = gg
                else:
                    sc /= numpy.array([len(s) for s in sample]).astype('float32')
                    ss = sample[sc.argmin()]
                    act = acts[sc.argmin()]
                    gg_ = gg[sc.argmin()]

                if model_options['stochastic']:
                    ss0 = sample0
                else:
                    sc0 /= numpy.array([len(s) for s in sample0]).astype('float32')
                    ss0  = sample0[sc0.argmin()]

                _ss = []
                for ii, si in enumerate(ss):
                    if si < model_options['voc_sizes'][1]:
                        _ss.append(si)
                    else:
                        offset = si - model_options['voc_sizes'][1]
                        _ss.append(sy2[jj][offset])

                # print 'Sample-CR {}: {}'.format(jj, idx2seq(_ss, 1))
                print 'NMT Model {}: {}'.format(jj, idx2seq(ss0, 1))
                print 'Copy Prob {}: {}'.format(jj, idx2seq(_ss, 1, act))
                print 'Copy Gate {}: {}'.format(jj, idx2seq(_ss, 1, gg_))
                print

        # validate model on validation set and early stop if necessary
        # if numpy.mod(uidx, validFreq) == 0:
        #    # use_noise.set_value(0.)
        #    valid_errs = validate(funcs, model_options, valid, False)
        #    valid_err  = valid_errs.mean()
        #    history_errs.append(valid_err)

        #    if numpy.isnan(valid_err):
        #        print 'NaN detected'
        #        sys.exit(-1)

        #    print 'Valid ', valid_err

        # validate model with BLEU
        pass

        # finish after this many updates
        if uidx >= finish_after:
            print 'Finishing after %d iterations!' % uidx
            estop = True
            break

    print 'Seen %d samples' % n_samples

    if estop:
        break

if best_p is not None:
    zipp(best_p, tparams)

valid_err = validate(funcs, model_options, valid).mean()
print 'Valid ', valid_err

params = copy.copy(best_p)
numpy.savez(saveto, zipped_params=best_p,
            history_errs=history_errs,
            uidx=uidx,
            **params)


