import ROOT

def create_example(ws_name='ws', nb=100, ns=30, sigma_nb=0.2):
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
    ws.factory('expr::nb("@0 * (1 + @1 * @2)", {ns, sigma_nb, theta_nb})')
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


if __name__ == "__main__":
    ws = create_example()
    ws.Print()
    ws.writeToFile('simple_counting_example.root')

"""
ROOT.gROOT.ProcessLine(".L StandardHypoTestInvDemo.C")
ROOT.StandardHypoTestInvDemo('example.root', 'example', 'model_config', 'bmodel', 'data_toy_nosignal', 2, 3, True, 20, 0.1, 10)
"""
