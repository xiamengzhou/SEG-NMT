# setup the training and testing details in this file
def setup_fren0():
    # home = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT'
    home  = '/root/workspace/TMNMT'
    model = '/root/disk/scratch/model-tmnmt'
    # name  = 'TM2.A0'
    name  = 'TM2.B5'

    # home   = '/scratch/jg5223/exp/TMNMT'
    config = {
        # train phase
        'name': name,
        'saveto': model + '/' + name + '_',
        'datasets': [home + '/.dataset/tm2.enfr/train.fr.top5.shuf.tok',          # source
                     home + '/.dataset/tm2.enfr/train.en.top5.shuf.tok',          # target
                     home + '/.dataset/tm2.enfr/train.fr.top5.matched.shuf.tok',  # source-TM
                     home + '/.dataset/tm2.enfr/train.en.top5.matched.shuf.tok'   # target-TM
                     ],

        'valid_datasets': [home + '/.dataset/tm2.fren/devset.fr.tok',
                           home + '/.dataset/tm2.fren/devset.en.tok',
                           home + '/.dataset/tm2.fren/devset.fr.matched.tok',
                           home + '/.dataset/tm2.fren/devset.en.matched.tok'
                           ],

        'dictionaries': [home + '/.dataset/tm2.enfr/train.fr.top5.shuf.tok.pkl',
                         home + '/.dataset/tm2.enfr/train.en.top5.shuf.tok.pkl',
                         home + '/.dataset/tm2.enfr/train.fr.top5.shuf.tok.pkl',
                         home + '/.dataset/tm2.enfr/train.en.top5.shuf.tok.pkl'
                         ],

        'voc_sizes': [20000, 20000, 20000, 20000],
        'maxlen': 50,

        # baseline models
        'baseline_xy': model + '/baseline_fren.npz',

        # test phase
        'trans_from': home + '/.dataset/tm2.fren/devset.fr.tok',
        'tm_source':  home + '/.dataset/tm2.fren/devset.fr.matched.tok',
        'tm_target':  home + '/.dataset/tm2.fren/devset.en.matched.tok',
        'trans_ref':  home + '/.dataset/tm2.fren/devset.en.tok',
        'trans_to':   home + '/.translate/' + name + '.dev.translate'
    }
    return config


def setup_fren():
    # home = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT'
    home  = '/root/workspace/TMNMT'
    model = '/root/disk/scratch/model-tmnmt'
    name  = 'TM2.B7'

    # home   = '/scratch/jg5223/exp/TMNMT'
    config = {
        # train phase
        'name': name,
        'saveto': model + '/' + name + '_',
        'datasets': [home + '/.dataset/top5k.fren/train.fr.top5.shuf.tok',          # source
                     home + '/.dataset/top5k.fren/train.en.top5.shuf.tok',          # target
                     home + '/.dataset/top5k.fren/train.fr.top5.matched.shuf.tok',  # source-TM
                     home + '/.dataset/top5k.fren/train.en.top5.matched.shuf.tok'   # target-TM
                     ],

        'valid_datasets': [home + '/.dataset/top5k.fren/devset.fr.tok',
                           home + '/.dataset/top5k.fren/devset.en.tok',
                           home + '/.dataset/top5k.fren/devset.fr.matched.tok',
                           home + '/.dataset/top5k.fren/devset.en.matched.tok'
                           ],

        'dictionaries': [home + '/.dataset/top5k.fren/train.fr.top5.shuf.tok.pkl',
                         home + '/.dataset/top5k.fren/train.en.top5.shuf.tok.pkl',
                         home + '/.dataset/top5k.fren/train.fr.top5.shuf.tok.pkl',
                         home + '/.dataset/top5k.fren/train.en.top5.shuf.tok.pkl'
                         ],

        'voc_sizes': [20000, 20000, 20000, 20000],
        'maxlen': 50,

        # baseline models
        'baseline_xy': model + '/baseline_fren.npz',

        # test phase
        'trans_from': home + '/.dataset/top5k.fren/devset.fr.tok',
        'tm_source':  home + '/.dataset/top5k.fren/devset.fr.matched.tok',
        'tm_target':  home + '/.dataset/top5k.fren/devset.en.matched.tok',
        'trans_ref':  home + '/.dataset/top5k.fren/devset.en.tok',
        'trans_to':   home + '/.translate/' + name + '.dev.translate'
    }
    return config


def setup_enfr():
    home  = '/home/thoma/work/TMNMT'
    model = '/home/thoma/scratch/tmnmt'
    #name  = 'TM2.v1'
    name  = 'TM2.A7'

    config = {
        # train phase
        'name': name,
        'saveto': model + '/' + name + '_',
        'datasets': [home + '/.dataset/tm2.fren/train.en.top5.shuf.tok',          # source
                     home + '/.dataset/tm2.fren/train.fr.top5.shuf.tok',          # target
                     home + '/.dataset/tm2.fren/train.en.top5.matched.shuf.tok',  # source-TM
                     home + '/.dataset/tm2.fren/train.fr.top5.matched.shuf.tok'   # target-TM
                     ],

        'valid_datasets': [home + '/.dataset/tm2.fren/devset.enfr.en.tok',
                           home + '/.dataset/tm2.fren/devset.enfr.fr.tok',
                           home + '/.dataset/tm2.fren/devset.enfr.en.matched.tok',
                           home + '/.dataset/tm2.fren/devset.enfr.fr.matched.tok'
                           ],

        'dictionaries': [home + '/.dataset/tm2.fren/train.en.top5.shuf.tok.pkl',
                         home + '/.dataset/tm2.fren/train.fr.top5.shuf.tok.pkl',
                         home + '/.dataset/tm2.fren/train.en.top5.shuf.tok.pkl',
                         home + '/.dataset/tm2.fren/train.fr.top5.shuf.tok.pkl'
                         ],

        'voc_sizes': [20000, 20000, 20000, 20000],
        'maxlen': 50,

        # baseline models
        'baseline_xy': model + '/baseline_enfr.bs64.npz',

        # test phase
        'trans_from': home + '/.dataset/tm2.fren/devset.enfr.en.tok',
        'tm_source':  home + '/.dataset/tm2.fren/devset.enfr.en.matched.tok',
        'tm_target':  home + '/.dataset/tm2.fren/devset.enfr.fr.matched.tok',
        'trans_ref':  home + '/.dataset/tm2.fren/devset.enfr.fr.tok',
        'trans_to':   home + '/.translate/' + name + '.dev.translate'
    }
    return config


def setup_fren_bpe_fusion():
    # home  = '/root/workspace/TMNMT'
    # model = '/root/disk/scratch/model-tmnmt'
    home  = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT'
    model = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT/.model'
    name  = 'TM2.B7.bpe.fusion'

    # home   = '/scratch/jg5223/exp/TMNMT'
    config = {
        # train phase
        'name': name,
        'saveto': model + '/' + name + '_',
        'datasets': [home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe',          # source
                     home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe',          # target
                     home + '/.dataset/top5k.fren.bpe/train.fr.top5.matched.shuf.tok.bpe',  # source-TM
                     home + '/.dataset/top5k.fren.bpe/train.en.top5.matched.shuf.tok.bpe'   # target-TM
                     ],

        'valid_datasets': [home + '/.dataset/top5k.fren.bpe/devset.fr.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.en.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.fr.matched.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.en.matched.tok.bpe'
                           ],

        'dictionaries': [home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe.pkl'
                         ],

        'voc_sizes': [20000, 20000, 20000, 20000],
        'maxlen': 80,

        # baseline models
        'baseline_xy': model + '/baseline_fren.bpe.npz',

        # test phase
        'trans_from': home + '/.dataset/top5k.fren.bpe/devset.fr.tok.bpe',
        'tm_source':  home + '/.dataset/top5k.fren.bpe/devset.fr.matched.tok.bpe',
        'tm_target':  home + '/.dataset/top5k.fren.bpe/devset.en.matched.tok.bpe',
        'trans_ref':  home + '/.dataset/top5k.fren/devset.en.tok',
        'trans_to':   home + '/.translate/' + name + '.dev.translate',

        # multi-tm test
        'tm_source_full': home + '/.dataset/top5k.fren.bpe/train.fr.top1.tok.bpe',
        'tm_target_full': home + '/.dataset/top5k.fren.bpe/train.en.top1.tok.bpe',
        'tm_rank':   home + '/.dataset/top5k.fren/match_top100.pkl',
        'tm_record': home + '/.dataset/top5k.fren/match_record5.pkl'

    }
    return config


def setup_fren_bpe_fusion2():
    # home  = '/root/workspace/TMNMT'
    # model = '/root/disk/scratch/model-tmnmt'
    home  = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT'
    model = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT/.model'
    name  = 'TM2.B7.bpe.fusion'

    # home   = '/scratch/jg5223/exp/TMNMT'
    config = {
        # train phase
        'name': name,
        'saveto': model + '/' + name + '_',
        'datasets': [home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe',          # source
                     home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe',          # target
                     home + '/.dataset/top5k.fren.bpe/train.fr.top5.matched.shuf.tok.bpe',  # source-TM
                     home + '/.dataset/top5k.fren.bpe/train.en.top5.matched.shuf.tok.bpe'   # target-TM
                     ],

        'valid_datasets': [home + '/.dataset/top5k.fren.bpe/devset.fr.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.en.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.fr.matched.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.en.matched.tok.bpe'
                           ],

        'dictionaries': [home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe.pkl'
                         ],

        'voc_sizes': [20000, 20000, 20000, 20000],
        'maxlen': 80,
        'use_pretrain': True,

        # baseline models
        'baseline_xy': model + '/baseline_fren.bpe.iter200000.npz',

        # test phase
        'trans_from': home + '/.dataset/top5k.fren.bpe/devset.fr.tok.bpe',
        'tm_source':  home + '/.dataset/top5k.fren.bpe/devset.fr.matched.tok.bpe',
        'tm_target':  home + '/.dataset/top5k.fren.bpe/devset.en.matched.tok.bpe',
        'trans_ref':  home + '/.dataset/top5k.fren.bpe/devset.en.tok',
        'trans_to':   home + '/.translate/' + name + '.dev.translate',

        # multi-tm test
        'tm_source_full': home + '/.dataset/top5k.fren.bpe/train.fr.top1.tok.bpe',
        'tm_target_full': home + '/.dataset/top5k.fren.bpe/train.en.top1.tok.bpe',
        'tm_rank':   home + '/.dataset/top5k.fren/match_top100.pkl',
        'tm_record': home + '/.dataset/top5k.fren/match_record5.pkl'

    }
    return config


def setup_fren_bpe_fusion3():
    # home  = '/root/workspace/TMNMT'
    # model = '/root/disk/scratch/model-tmnmt'
    home  = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT'
    model = '/misc/kcgscratch1/ChoGroup/thoma_exp/memory/TMNMT/.model'
    name  = 'TM2.B7.bpe.fusion'

    # home   = '/scratch/jg5223/exp/TMNMT'
    config = {
        # train phase
        'name': name,
        'saveto': model + '/' + name + '_',
        'datasets': [home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe',          # source
                     home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe',          # target
                     home + '/.dataset/top5k.fren.bpe/train.fr.top5.matched.shuf.tok.bpe',  # source-TM
                     home + '/.dataset/top5k.fren.bpe/train.en.top5.matched.shuf.tok.bpe'   # target-TM
                     ],

        'valid_datasets': [home + '/.dataset/top5k.fren.bpe/devset.fr.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.en.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.fr.matched.tok.bpe',
                           home + '/.dataset/top5k.fren.bpe/devset.en.matched.tok.bpe'
                           ],

        'dictionaries': [home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.fr.top5.shuf.tok.bpe.pkl',
                         home + '/.dataset/top5k.fren.bpe/train.en.top5.shuf.tok.bpe.pkl'
                         ],

        'voc_sizes': [20000, 20000, 20000, 20000],
        'maxlen': 80,
        'use_pretrain': True,
        'elem_gates': True,


        # baseline models
        'baseline_xy': model + '/baseline_fren.bpe.iter200000.npz',

        # test phase
        'trans_from': home + '/.dataset/top5k.fren.bpe/devset.fr.tok.bpe',
        'tm_source':  home + '/.dataset/top5k.fren.bpe/devset.fr.matched.tok.bpe',
        'tm_target':  home + '/.dataset/top5k.fren.bpe/devset.en.matched.tok.bpe',
        'trans_ref':  home + '/.dataset/top5k.fren/devset.en.tok',
        'trans_to':   home + '/.translate/' + name + '.dev.translate',

        # multi-tm test
        'tm_source_full': home + '/.dataset/top5k.fren.bpe/train.fr.top1.tok.bpe',
        'tm_target_full': home + '/.dataset/top5k.fren.bpe/train.en.top1.tok.bpe',
        'tm_rank':   home + '/.dataset/top5k.fren/match_top100.pkl',
        'tm_record': home + '/.dataset/top5k.fren/match_record5.pkl'

    }
    return config


def setup(pair='fren'):
    # basic setting
    config = {

        # model details
        'encoder':     'gru',
        'decoder':     'gru_cond',
        'dim_word':     512,
        'dim':          1024,

        # training details
        'optimizer':   'adam',
        'decay_c':      0.,
        'clip_c':       1.,
        'use_dropout':  False,
        'lrate':        0.0001,
        'patience':     1000,

        'batch_size':   32,
        'valid_batch_size': 32,

        'validFreq':    250,
        'bleuFreq':     5000,
        'saveFreq':     250,
        'sampleFreq':   20,

        'overwrite':    False,
        'reload_':      True,

        'use_pretrain': False,
        'only_train_g': False,
        'diagonal':     True,
        'eye':          True,
        'cos_sim':      False,

        'use_coverage': True,
        'nn_coverage':  False,
        'cov_dim':      10,

        'elem_gates':   False,

        'stochastic':   False,
        'build_gate':   True,
        'gate_loss':    False,
        'gate_lambda':  0.1,

        'disable_bleu': True,

        # testing details
        'beamsize':     5,
        'normalize':    True,
        'd_maxlen':     200,
        'check_bleu':   True,

        # remote monitor (tensorboard)
        'remote':       True,
        'address':      '147.8.182.14',
        'port':         8889
    }

    # get dataset info
    config.update(eval('setup_{}'.format(pair))())

    # get full model name
    config['saveto'] += '{}.{}.{}-{}.npz'.format(
            pair, 'ff' if config['use_pretrain'] else 'ss',
            config['batch_size'], config['maxlen']
        )
    print 'start {}'.format(config['saveto'])
    return config
