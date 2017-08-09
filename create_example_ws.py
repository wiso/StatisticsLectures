import ROOT


def safe_factory(func):
    def wrapper(self, *args):
        result = func(self, *args)
        if not result:
            raise ValueError('invalid factory input "%s"' % args)
        return result
    return wrapper

ROOT.RooWorkspace.factory = safe_factory(ROOT.RooWorkspace.factory)

def safe_decorator(func):
    def wrapper(self, *args):
        result = func(self, *args)
        if not result:
            raise ValueError('cannot find %s' % args[0])
        return result
    return wrapper

ROOT.RooWorkspace.data = safe_decorator(ROOT.RooWorkspace.data)
ROOT.RooWorkspace.obj = safe_decorator(ROOT.RooWorkspace.obj)
ROOT.RooWorkspace.var = safe_decorator(ROOT.RooWorkspace.var)
ROOT.RooWorkspace.pdf = safe_decorator(ROOT.RooWorkspace.pdf)


def create_example_counting_oneregion_uncertainty(ws_name='ws', nb=100, ns=30, sigma_nb=0.1):
    """
    nb = number of expected background
    ns = number of expected signal (under signal hypothesis)
    sigma_nb = uncertainty on the expected background
    """
    ws = ROOT.RooWorkspace(ws_name)
    ws.factory('ns[%d, 0, 100]' % ns)
    ws.factory('nobs[0, %d]' % ((nb + ns) * 100))
    ws.factory('nb_expected[%d]' % nb)
    ws.factory('sigma_nb[%f]' % sigma_nb)
    ws.factory('theta_nb[0, -5, 5]')
    ws.factory('expr::nb("@0 * (1 + @1 * @2)", {nb_expected, sigma_nb, theta_nb})')
    ws.factory('sum::nexp(ns, nb)')
    ws.factory('Poisson::pdf_phys(nobs, nexp)')
    ws.factory('Gaussian::constr_nb(global_nb[0, -5, 5], theta_nb, 1)')
    ws.factory('PROD:pdf(pdf_phys, constr_nb)')

    model_config = ROOT.RooStats.ModelConfig('model_config', ws)
    model_config.SetParametersOfInterest('ns')
    model_config.SetPdf('pdf')
    model_config.SetNuisanceParameters('theta_nb')
    model_config.SetGlobalObservables('global_nb')
    model_config.SetObservables('nobs')
    model_config.SetSnapshot(ROOT.RooArgSet(ws.var('ns')))

    data_toy_signal = ws.pdf('pdf_phys').generate(ROOT.RooArgSet(ws.var('nobs')), 1)
    data_toy_signal.SetName('data_toy_signal')

    ws.var('ns').setVal(0)
    data_toy_nosignal = ws.pdf('pdf_phys').generate(ROOT.RooArgSet(ws.var('nobs')), 1)
    data_toy_nosignal.SetName('data_toy_nosignal')

    bmodel = model_config.Clone('bmodel')
    bmodel.SetSnapshot(ROOT.RooArgSet(ws.var('ns')))

    getattr(ws, 'import')(model_config)
    getattr(ws, 'import')(bmodel)
    getattr(ws, 'import')(data_toy_signal)
    getattr(ws, 'import')(data_toy_nosignal)

    return ws


def create_example_onoff(ws_name='ws', nb=9, ns=6, tau=1):
    """
    nb = number of expected background in the signal region
    ns = number of expected signal (under signal hypothesis)
    tau = scale factor for the background in the control-region
          (nb in the control-region: nb * tau)
    """
    ws = ROOT.RooWorkspace(ws_name)
    ws.factory('ns[%d, 0, %d]' % (ns, ns * 100))
    ws.factory('nb_sr[%d, 0, %d]' % (nb, nb * 100))
    ws.factory('nobs_sr[0, %d]' % ((nb + ns) * 100))
    ws.factory('nobs_cr[0, %d]' % (nb * tau * 100))
    ws.factory('sum::nexp_sr(ns, nb_sr)')
    ws.factory('Poisson::pdf_sr(nobs_sr, nexp_sr)')
    ws.factory('prod:nb_cr(tau[%f], nb_sr)' % tau)
    ws.factory('Poisson::pdf_cr(nobs_cr, nb_cr)')
    ws.factory('PROD:pdf(pdf_sr, pdf_cr)')

    model_config = ROOT.RooStats.ModelConfig('model_config', ws)
    model_config.SetParametersOfInterest('ns')
    model_config.SetPdf('pdf')
    model_config.SetNuisanceParameters('nb_sr')
    model_config.SetObservables('nobs_sr,nobs_cr')
    model_config.SetSnapshot(ROOT.RooArgSet(ws.var('ns')))

    data_toy_signal = ws.pdf('pdf').generate(model_config.GetObservables(), 1)
    data_toy_signal.SetName('data_toy_signal')

    ws.var('ns').setVal(0)
    data_toy_nosignal = ws.pdf('pdf').generate(model_config.GetObservables(), 1)
    data_toy_nosignal.SetName('data_toy_nosignal')

    bmodel = model_config.Clone('bmodel')
    bmodel.SetSnapshot(ROOT.RooArgSet(ws.var('ns')))

    getattr(ws, 'import')(model_config)
    getattr(ws, 'import')(bmodel)
    getattr(ws, 'import')(data_toy_signal)
    getattr(ws, 'import')(data_toy_nosignal)

    return ws






if __name__ == "__main__":
    example = 'onoff'
    if example == 'onoff':
        ws = create_example_onoff()
        ws.writeToFile('ws_onoff.root')
    else:
        ws = create_example_counting_oneregion_uncertainty
        ws.writeToFile('simple_counting_example.root')
    ws.Print()


"""
ROOT.gROOT.ProcessLine(".L StandardHypoTestInvDemo.C")
ROOT.StandardHypoTestInvDemo('simple_counting_example.root', 'ws', 'model_config', 'bmodel', 'data_toy_nosignal', 2, 3, True, 20, 0.1, 100)
"""
