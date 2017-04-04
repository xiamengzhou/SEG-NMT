'''
Translates a source file using a translation model.
'''
import argparse
import theano
import numpy
import time
import os
import cPickle as pkl
from layer import *
from nmt import (build_sampler, gen_sample, gen_sample_memory, load_params,
                 init_params, init_tparams, build_networks)
from setup import setup


def translate_model(queue, funcs, tparams, options, k,
                    normalize, m=0, d_maxlen=200):

    use_noise = theano.shared(numpy.float32(0.))
    from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
    trng = RandomStreams(19920206)

    def _translate(seq_x1, seq_x2, seq_y2):
        # sample given an input sequence and obtain scores
        sample, score, action, gating = \
                gen_sample_memory(tparams, funcs,
                                  numpy.array(seq_x1).reshape([len(seq_x1), 1]),
                                  numpy.array(seq_x2).reshape([len(seq_x2), 1]),
                                  numpy.array(seq_y2).reshape([len(seq_y2), 1]),
                                  options, rng=trng, m=m, k=k, maxlen=d_maxlen,
                                  stochastic=options['stochastic'], argmax=True)

        # normalize scores according to sequence lengths
        if k > 1:
            if normalize:
                lengths = numpy.array([len(s) for s in sample])
                score  /= lengths

            sidx   = numpy.argmin(score)
            sample, score, action, gating = \
                    sample[sidx], score[sidx], action[sidx], gating[sidx]

        return sample, score, action, gating

    rqueue = []
    time1  = time.time()
    for req in queue:
        idx, sx1, sx2, sy2 = req[0], req[1], req[2], req[3]
        x1 = map(lambda ii: ii if ii < options['voc_sizes'][0] else 1, sx1)
        x2 = map(lambda ii: ii if ii < options['voc_sizes'][2] else 1, sx2)
        y2 = map(lambda ii: ii if ii < options['voc_sizes'][3] else 1, sy2)

        if idx % 10 == 0:
            print '[test] complete:{}, {}s'.format(idx, time.time() - time1)

        seq, ss, acts, gs = _translate(x1, x2, y2)
        sseq = map(lambda ii: ii if ii < options['voc_sizes'][1] else sy2[ii-options['voc_sizes'][1]], seq)

        rqueue.append((sseq, ss, acts, gs))

    print '[test] complete:{}, {}s'.format(idx, time.time() - time1)
    return rqueue


def go(model, dictionary, dictionary_target,
       source_file_x1, source_file_x2, source_file_y2, reference_file_y1,
       saveto, k=5, normalize=False, d_maxlen=200,
       steps=None, max_steps=None, start_steps=0, sleep=1000,
       *args, **kwargs):

    # inter-step
    step_test = 0

    # load model model_options
    with open('%s.pkl' % model, 'rb') as f:
        options = pkl.load(f)

    # load source dictionary and invert
    with open(dictionary, 'rb') as f:
        word_dict = pkl.load(f)
    word_idict = dict()
    for kk, vv in word_dict.iteritems():
        word_idict[vv] = kk
    word_idict[0] = '<eos>'
    word_idict[1] = 'UNK'

    # load target dictionary and invert
    with open(dictionary_target, 'rb') as f:
        word_dict_trg = pkl.load(f)
    word_idict_trg = dict()
    for kk, vv in word_dict_trg.iteritems():
        word_idict_trg[vv] = kk
    word_idict_trg[0] = '<eos>'
    word_idict_trg[1] = 'UNK'

    # utility function
    def _seqs2words(caps):
        capsw = []
        for cc in caps:
            ww = []
            for w in cc:
                if w == 0:
                    break
                ww.append(word_idict_trg[w])
            capsw.append(' '.join(ww))
        return capsw

    def _send_jobs(fname_x1, fname_x2, fname_y2):
        queue_x1 = []
        queue_x2 = []
        queue_y2 = []
        queue = []
        with open(fname_x1, 'r') as f:
            for idx, line in enumerate(f):

                words = line.strip().split()
                x1 = map(lambda w: word_dict[w] if w in word_dict else 1, words)
                x1 += [0]
                queue_x1.append((idx, x1))

        with open(fname_x2, 'r') as f:
            for idx, line in enumerate(f):

                words = line.strip().split()
                x2 = map(lambda w: word_dict[w] if w in word_dict else 1, words)
                x2 += [0]
                queue_x2.append((idx, x2))

        with open(fname_y2, 'r') as f:
            for idx, line in enumerate(f):

                words = line.strip().split()
                y2 = map(lambda w: word_dict_trg[w] if w in word_dict_trg else 1, words)
                y2 += [0]
                queue_y2.append((idx, y2))

        for i, (x1, x2, y2) in enumerate(zip(queue_x1, queue_x2, queue_y2)):
            queue.append((i, x1[1], x2[1], y2[1]))

        return queue


    print '[test] build the model'
    funcs, tparams = build_networks(options, model, train=False)

    if steps is None:
        print '[test] start translating ', source_file_x1, '...to...', saveto
        queue = _send_jobs(source_file_x1, source_file_x2, source_file_y2)
        rets  = translate_model(queue, funcs, tparams, options, k, normalize, 0, d_maxlen)
        sseqs, ss, acts, gs = zip(*rets)

        trans = _seqs2words(sseqs)
        with open(saveto, 'w') as f:
            print >>f, '\n'.join(trans)
        print 'Done'

        pkl.dump(rets, open(saveto + '.pkl', 'w'))
        print 'All Done'

    else:
        step_test = start_steps
        if step_test == 0:
            step_test += steps

        while step_test < max_steps:

            # check if the check-point is saved
            checkpoint = '{}.iter{}.npz'.format(os.path.splitext(model)[0], step_test)
            if not os.path.exists(checkpoint):
                print '[test] Did not find checkpoint: {}. I want sleep {}s.'.format(checkpoint, sleep)

                time.sleep(sleep)

            else:

                transto = saveto + '.iter={}'.format(step_test)
                print '[test] start translating ', source_file_x1, '...to...', transto

                if os.path.exists(transto):
                    print 'we found translated files...skip'
                else:
                    print '[test] Load check-point: {}'.format(checkpoint),
                    zipp(load_params(checkpoint, unzip(tparams)), tparams)
                    print 'done.'

                    queue = _send_jobs(source_file_x1, source_file_x2, source_file_y2)
                    rets = translate_model(queue, funcs, tparams, options, k, normalize, 0, d_maxlen)
                    sseqs, ss, acts, gs = zip(*rets)

                    trans = _seqs2words(sseqs)
                    with open(transto, 'w') as f:
                        print >> f, '\n'.join(trans)
                    print 'Done'

                    pkl.dump(rets, open(transto + '.pkl', 'w'))

                # compute BLEU score.
                ref = reference_file_y1

                print '[test] compute BLEU score for {} <-> {}'.format(transto, ref)
                # os.system("ed -i 's/@@ //g' {}".format(hyp))
                os.system('perl ./data/multi-bleu.perl {0} < {1} | tee {1}.score'.format(ref, transto))

                print 'Done at iter={}'.format(step_test)
                step_test += steps

            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=str, default='fren')
    parser.add_argument('-p', type=str, default='round')
    args = parser.parse_args()

    config = setup(args.m)
    if args.p == 'round':
        print 'ROUND-MODE'
        go(config['saveto'],
           config['dictionaries'][0],
           config['dictionaries'][1],
           config['trans_from'],
           config['tm_source'],
           config['tm_target'],
           config['trans_ref'],
           config['trans_to'],
           config['beamsize'],
           config['normalize'],
           config['d_maxlen'],
           steps=2500, max_steps=1000000, start_steps=0,
           sleep=600)
    else:
        print 'TEST-MODE'
        go(config['saveto'],
           config['dictionaries'][0],
           config['dictionaries'][1],
           config['trans_from'],
           config['tm_source'],
           config['tm_target'],
           config['trans_to'],
           config['beamsize'],
           config['normalize'],
           config['d_maxlen'])

    print 'all done'
