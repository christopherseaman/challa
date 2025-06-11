import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from k01_power_analysis import K01PowerAnalysis
import config

@pytest.fixture
def analysis():
    return K01PowerAnalysis()

def test_dyadic_power_apim_defaults(analysis):
    params = config.aim3_params
    results = analysis.dyadic_power_apim(
        params['n_couples'],
        params['baseline_ipv_rate'],
        params['actor_effect_OR'],
        params['partner_effect_OR'],
        params['icc_partners'],
        params['alpha']
    )
    assert pytest.approx(results['actor_power'], rel=1e-2) == 0.945
    assert pytest.approx(results['partner_power'], rel=1e-3) == 0.998
    assert results['design_effect'] == pytest.approx(1 + params['icc_partners'])
    assert results['n_effective'] == pytest.approx(2 * params['n_couples'] / (1 + params['icc_partners']))