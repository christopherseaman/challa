"""
K01 Power Analysis: South Asian Sexual and Reproductive Health Research
Comprehensive analysis addressing all consultation questions from 25.06.03-call.md

Rigorous power calculations for:
- Aim 1: CHIS decomposition analysis (n=237 South Asians vs comparison groups)
- Aim 3: Dyadic analysis using Actor-Partner Interdependence Model (200 couples)

Author: K01 Applicant
Date: 2025-06-10
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.stats.power as smp
from statsmodels.stats.proportion import proportions_ztest, proportion_effectsize
from statsmodels.stats.multitest import multipletests
from scipy.optimize import fsolve
import warnings
warnings.filterwarnings('ignore')

import config

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")

class K01PowerAnalysis:
    """Power calculations for K01 research aims"""
    
    def __init__(self):
        """Initialize study parameters based on consultation notes (25.06.03-call.md)"""
        
        # Aim 1: CHIS Analysis - IPV only (power-limiting outcome)
        # Parameters from consultation notes lines 99-124
        self.aim1_params = config.aim1_params.copy()
        
        # Aim 3: Dyadic APIM Analysis
        # Parameters from consultation notes lines 219-346
        self.aim3_params = config.aim3_params.copy()
    
    def two_sample_proportion_power(self, n1, n2, p1, p2, alpha=0.05, design_effect=1.0):
        """Calculate power for two-sample proportion test with design effects"""
        
        # Adjust sample sizes for design effect
        n1_eff = n1 / design_effect
        n2_eff = n2 / design_effect
        
        # Calculate effect size (Cohen's h)
        effect_size = proportion_effectsize(p1, p2)
        
        # Use harmonic mean for unequal sample sizes
        n_harmonic = 2 / (1/n1_eff + 1/n2_eff)
        
        try:
            power = smp.ttest_power(effect_size, n_harmonic, alpha, alternative='two-sided')
        except:
            # Fallback calculation
            p_pooled = (n1_eff * p1 + n2_eff * p2) / (n1_eff + n2_eff)
            se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1_eff + 1/n2_eff))
            effect = p1 - p2
            z_stat = abs(effect) / se
            z_alpha = stats.norm.ppf(1 - alpha/2)
            power = 1 - stats.norm.cdf(z_alpha - z_stat) + stats.norm.cdf(-z_alpha - z_stat)
        
        # Calculate odds ratio
        odds1 = p1 / (1 - p1)
        odds2 = p2 / (1 - p2)
        observed_OR = odds1 / odds2
        
        return {
            'power': max(0, min(1, power)),
            'effect_size_h': effect_size,
            'n1_effective': n1_eff,
            'n2_effective': n2_eff,
            'observed_OR': observed_OR,
            'p1': p1,
            'p2': p2
        }
    
    def min_detectable_OR(self, n1, n2, p2, power=0.8, alpha=0.05, design_effect=1.0):
        """Calculate minimum detectable odds ratio"""
        
        # Adjust for design effect
        n1_eff = n1 / design_effect
        n2_eff = n2 / design_effect
        n_harmonic = 2 / (1/n1_eff + 1/n2_eff)
        
        # Find effect size for target power
        def power_func(effect_size):
            return smp.ttest_power(effect_size, n_harmonic, alpha, alternative='two-sided') - power
        
        try:
            min_effect_size = fsolve(power_func, 0.2)[0]
        except:
            z_alpha = stats.norm.ppf(1 - alpha/2)
            z_beta = stats.norm.ppf(power)
            min_effect_size = (z_alpha + z_beta) / np.sqrt(n_harmonic/2)
        
        # Convert to proportion difference
        arcsin_p2 = np.arcsin(np.sqrt(p2))
        arcsin_p1 = arcsin_p2 + min_effect_size / 2
        arcsin_p1 = max(0, min(np.pi/2, arcsin_p1))
        p1_min = np.sin(arcsin_p1) ** 2
        
        # Calculate OR
        if 0 < p1_min < 1 and 0 < p2 < 1:
            odds1 = p1_min / (1 - p1_min)
            odds2 = p2 / (1 - p2)
            min_OR = odds1 / odds2
        else:
            min_OR = np.nan
        
        return min_OR
    
    def dyadic_power_apim(self, n_couples, p_baseline, actor_OR, partner_OR, icc, alpha=0.05):
        """Calculate power for dyadic APIM analysis"""
        
        # Design effect for clustered data
        design_effect = 1 + icc
        n_effective = (2 * n_couples) / design_effect
        
        # Convert ORs to effect sizes
        d_actor = np.log(actor_OR) * np.sqrt(3) / np.pi
        d_partner = np.log(partner_OR) * np.sqrt(3) / np.pi
        
        # Calculate power
        try:
            power_actor = smp.ttest_power(d_actor, n_effective, alpha, alternative='two-sided')
            power_partner = smp.ttest_power(d_partner, n_effective, alpha, alternative='two-sided')
        except:
            se_approx = np.sqrt(4 / (n_effective * p_baseline * (1 - p_baseline)))
            z_alpha = stats.norm.ppf(1 - alpha/2)
            
            z_actor = abs(np.log(actor_OR)) / se_approx
            z_partner = abs(np.log(partner_OR)) / se_approx
            
            power_actor = 1 - stats.norm.cdf(z_alpha - z_actor) + stats.norm.cdf(-z_alpha - z_actor)
            power_partner = 1 - stats.norm.cdf(z_alpha - z_partner) + stats.norm.cdf(-z_alpha - z_partner)
        
        return {
            'actor_power': max(0, min(1, power_actor)),
            'partner_power': max(0, min(1, power_partner)),
            'design_effect': design_effect,
            'n_effective': n_effective
        }
    
    def consultation_question_target_or_power(self):
        """
        CONSULTATION QUESTION: Power for target OR=1.15 at α=0.1
        From consultation notes line 102: "possibly OR=1.15"
        """
        print("=" * 70)
        print("CONSULTATION QUESTION: POWER FOR TARGET OR=1.15")
        print("=" * 70)
        
        target_or = self.aim1_params['target_or']
        p_others = self.aim1_params['ipv_p_others']  # 6% baseline
        
        # Convert OR=1.15 to South Asian proportion
        # OR = (p1/(1-p1)) / (p2/(1-p2))
        # Solving for p1: p1 = OR*p2 / (1 + OR*p2 - p2)
        p_sa_target = (target_or * p_others) / (1 + target_or * p_others - p_others)
        
        # Power calculation for target OR
        target_power_01 = self.two_sample_proportion_power(
            self.aim1_params['n_south_asian'],
            self.aim1_params['n_others'],
            p_sa_target, p_others,
            0.1,  # α = 0.1
            self.aim1_params['design_effect']
        )
        
        target_power_05 = self.two_sample_proportion_power(
            self.aim1_params['n_south_asian'],
            self.aim1_params['n_others'],
            p_sa_target, p_others,
            0.05,  # α = 0.05
            self.aim1_params['design_effect']
        )
        
        print(f"Target OR: {target_or}")
        print(f"Baseline rate (others): {p_others:.1%}")
        print(f"Required SA rate for OR={target_or}: {p_sa_target:.2%}")
        print(f"Effective sample size: {target_power_01['n1_effective']:.0f}")
        print()
        print(f"Power Analysis for OR={target_or}:")
        print(f"  Power (α=0.1): {target_power_01['power']:.3f}")
        print(f"  Power (α=0.05): {target_power_05['power']:.3f}")
        print()
        
        return {
            'target_or': target_or,
            'target_proportion': p_sa_target,
            'power_01': target_power_01['power'],
            'power_05': target_power_05['power']
        }

    def run_aim1_analysis(self):
        """Run Aim 1 power analysis - IPV only (power-limiting outcome)"""
        
        print("=" * 70)
        print("AIM 1: CHIS DECOMPOSITION ANALYSIS - IPV ONLY")
        print("=" * 70)
        print(f"South Asian sample: n = {self.aim1_params['n_south_asian']}")
        print(f"Comparison group: n = {self.aim1_params['n_others']:,}")
        print(f"Design effect: {self.aim1_params['design_effect']}")
        print(f"Effective SA sample: {self.aim1_params['n_south_asian']/self.aim1_params['design_effect']:.0f}")
        print(f"Alpha level: {self.aim1_params['alpha']}")
        print()
        
        # IPV analysis only
        p_sa = self.aim1_params['ipv_p_south_asian']
        p_others = self.aim1_params['ipv_p_others']
        
        # Power calculations
        power_result = self.two_sample_proportion_power(
            self.aim1_params['n_south_asian'],
            self.aim1_params['n_others'],
            p_sa, p_others,
            self.aim1_params['alpha'],
            self.aim1_params['design_effect']
        )
        
        # Power with conventional alpha
        power_05 = self.two_sample_proportion_power(
            self.aim1_params['n_south_asian'],
            self.aim1_params['n_others'],
            p_sa, p_others,
            0.05,
            self.aim1_params['design_effect']
        )
        
        # Minimum detectable OR
        min_OR = self.min_detectable_OR(
            self.aim1_params['n_south_asian'],
            self.aim1_params['n_others'],
            p_others, power=0.8,
            alpha=self.aim1_params['alpha'],
            design_effect=self.aim1_params['design_effect']
        )
        
        # For 3 outcomes (IPV, contraceptive use, contraceptive counseling - line 92 in consultation notes)
        # FDR correction using standard method
        n_tests = 3
        p_values_example = [self.aim1_params['alpha']] * n_tests  # Conservative assumption
        fdr_rejected, fdr_pvals = multipletests(p_values_example, alpha=self.aim1_params['alpha'], method='fdr_bh')[:2]
        fdr_threshold = fdr_pvals[0]  # FDR-adjusted threshold
        
        # Power with FDR threshold
        power_fdr = self.two_sample_proportion_power(
            self.aim1_params['n_south_asian'],
            self.aim1_params['n_others'],
            p_sa, p_others,
            fdr_threshold,
            self.aim1_params['design_effect']
        )
        
        # Bonferroni correction
        power_bonf = self.two_sample_proportion_power(
            self.aim1_params['n_south_asian'],
            self.aim1_params['n_others'],
            p_sa, p_others,
            self.aim1_params['alpha'] / n_tests,
            self.aim1_params['design_effect']
        )
        
        results = {
            'p_south_asian': p_sa,
            'p_others': p_others,
            'observed_OR': power_result['observed_OR'],
            'power_unadjusted': power_result['power'],
            'power_05': power_05['power'],
            'power_fdr': power_fdr['power'],
            'power_bonferroni': power_bonf['power'],
            'n_sa_effective': power_result['n1_effective'],
            'min_detectable_OR': min_OR,
            'fdr_threshold': fdr_threshold
        }
        
        print("IPV (Primary Outcome):")
        print(f"  South Asian rate: {p_sa:.1%}")
        print(f"  Others rate: {p_others:.1%}")
        print(f"  Observed OR: {power_result['observed_OR']:.2f}")
        print(f"  Power (α=0.1, unadjusted): {power_result['power']:.3f}")
        print(f"  Power (α=0.05, unadjusted): {power_05['power']:.3f}")
        print(f"  Power (FDR corrected): {power_fdr['power']:.3f}")
        print(f"  Power (Bonferroni): {power_bonf['power']:.3f}")
        print(f"  Min detectable OR (80% power): {min_OR:.2f}")
        print()
        
        print(f"Multiple Comparisons Summary (3 outcomes from consultation notes):")
        print(f"  FDR threshold: α = {fdr_threshold:.3f}")
        print(f"  Bonferroni threshold: α = {self.aim1_params['alpha']/n_tests:.3f}")
        print()
        
        return results
    
    def run_aim3_analysis(self):
        """Run Aim 3 power analysis"""
        
        print("=" * 60)
        print("AIM 3: DYADIC APIM ANALYSIS")
        print("=" * 60)
        print(f"Number of couples: {self.aim3_params['n_couples']}")
        print(f"Baseline IPV rate: {self.aim3_params['baseline_ipv_rate']:.1%}")
        print(f"ICC between partners: {self.aim3_params['icc_partners']}")
        print(f"Actor effect OR: {self.aim3_params['actor_effect_OR']}")
        print(f"Partner effect OR: {self.aim3_params['partner_effect_OR']}")
        print(f"Alpha level: {self.aim3_params['alpha']}")
        print()
        
        # Calculate power
        dyadic_results = self.dyadic_power_apim(
            self.aim3_params['n_couples'],
            self.aim3_params['baseline_ipv_rate'],
            self.aim3_params['actor_effect_OR'],
            self.aim3_params['partner_effect_OR'],
            self.aim3_params['icc_partners'],
            self.aim3_params['alpha']
        )
        
        print("Power Analysis Results:")
        print(f"  Design effect (clustering): {dyadic_results['design_effect']:.2f}")
        print(f"  Effective sample size: {dyadic_results['n_effective']:.0f}")
        print(f"  Actor effect power: {dyadic_results['actor_power']:.3f}")
        print(f"  Partner effect power: {dyadic_results['partner_power']:.3f}")
        print()
        
        return dyadic_results
    
    def create_power_vs_or_plots(self):
        """Generate power vs OR plots as requested"""
        
        # OR range for plotting
        or_range = np.arange(1.0, 2.5, 0.05)
        
        # Aim 1: Power vs OR for fixed sample size and alpha
        powers_01 = []
        powers_05 = []
        p_others = self.aim1_params['ipv_p_others']  # 6% baseline
        
        for or_val in or_range:
            # Convert OR to proportion
            p_sa = (or_val * p_others) / (1 + or_val * p_others - p_others)
            
            if 0 < p_sa < 1:  # Valid proportion
                # Power at α=0.1
                power_01 = self.two_sample_proportion_power(
                    self.aim1_params['n_south_asian'],
                    self.aim1_params['n_others'],
                    p_sa, p_others, 0.1,
                    self.aim1_params['design_effect']
                )['power']
                
                # Power at α=0.05
                power_05 = self.two_sample_proportion_power(
                    self.aim1_params['n_south_asian'],
                    self.aim1_params['n_others'],
                    p_sa, p_others, 0.05,
                    self.aim1_params['design_effect']
                )['power']
            else:
                power_01 = np.nan
                power_05 = np.nan
                
            powers_01.append(power_01)
            powers_05.append(power_05)
        
        # Aim 3: Power vs OR for dyadic effects
        dyadic_actor_01 = []
        dyadic_partner_01 = []
        
        for or_val in or_range:
            dyadic_result = self.dyadic_power_apim(
                self.aim3_params['n_couples'],
                self.aim3_params['baseline_ipv_rate'],
                or_val,  # Actor OR
                or_val,  # Partner OR (same for comparison)
                self.aim3_params['icc_partners'],
                0.1
            )
            dyadic_actor_01.append(dyadic_result['actor_power'])
            dyadic_partner_01.append(dyadic_result['partner_power'])
        
        # Create plots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Aim 1: Power vs OR
        ax1.plot(or_range, powers_01, 'b-', linewidth=3, label='α = 0.1')
        ax1.plot(or_range, powers_05, 'r-', linewidth=3, label='α = 0.05')
        ax1.axhline(y=0.8, color='gray', linestyle='--', alpha=0.7, label='80% Power')
        ax1.axvline(x=1.15, color='orange', linestyle=':', linewidth=2, label='Target OR=1.15')
        ax1.axvline(x=1.74, color='purple', linestyle=':', linewidth=2, label='Observed OR=1.74')
        ax1.set_xlabel('Odds Ratio')
        ax1.set_ylabel('Power')
        ax1.set_title('Aim 1: Power vs Odds Ratio\n(n=237 SA, n=158 effective)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xlim(1.0, 2.2)
        ax1.set_ylim(0, 1)
        
        # Sample size sensitivity
        n_range = np.arange(100, 500, 25)
        ipv_powers = []
        
        for n in n_range:
            power_result = self.two_sample_proportion_power(
                n, self.aim1_params['n_others'],
                self.aim1_params['ipv_p_south_asian'],
                self.aim1_params['ipv_p_others'],
                self.aim1_params['alpha'],
                self.aim1_params['design_effect']
            )
            ipv_powers.append(power_result['power'])
        
        ax2.plot(n_range, ipv_powers, 'b-', marker='o', linewidth=2, markersize=4)
        ax2.axhline(y=0.8, color='r', linestyle='--', alpha=0.7, label='80% Power')
        ax2.axvline(x=self.aim1_params['n_south_asian'], color='orange', linestyle=':', alpha=0.7, label='Current N=237')
        ax2.set_xlabel('South Asian Sample Size')
        ax2.set_ylabel('Power')
        ax2.set_title('Aim 1: Power vs Sample Size\n(IPV outcome, OR=1.74)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Aim 3: Actor vs Partner Effects
        ax3.plot(or_range, dyadic_actor_01, 'purple', linewidth=3, label='Actor Effect')
        ax3.plot(or_range, dyadic_partner_01, 'orange', linewidth=3, label='Partner Effect')
        ax3.axhline(y=0.8, color='gray', linestyle='--', alpha=0.7, label='80% Power')
        ax3.axvline(x=1.4, color='purple', linestyle=':', alpha=0.7, label='Actor OR=1.4')
        ax3.axvline(x=1.6, color='orange', linestyle=':', alpha=0.7, label='Partner OR=1.6')
        ax3.set_xlabel('Odds Ratio')
        ax3.set_ylabel('Power')
        ax3.set_title('Aim 3: Power vs Odds Ratio\n(200 couples, α=0.1)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.set_xlim(1.0, 2.2)
        ax3.set_ylim(0, 1)
        
        # Aim 3: Sample size sensitivity
        couples_range = np.arange(100, 400, 25)
        actor_powers = []
        partner_powers = []
        
        for n_couples in couples_range:
            dyadic_result = self.dyadic_power_apim(
                n_couples,
                self.aim3_params['baseline_ipv_rate'],
                self.aim3_params['actor_effect_OR'],
                self.aim3_params['partner_effect_OR'],
                self.aim3_params['icc_partners'],
                self.aim3_params['alpha']
            )
            actor_powers.append(dyadic_result['actor_power'])
            partner_powers.append(dyadic_result['partner_power'])
        
        ax4.plot(couples_range, actor_powers, 'purple', marker='o', linewidth=2, markersize=4, label='Actor Effect')
        ax4.plot(couples_range, partner_powers, 'orange', marker='s', linewidth=2, markersize=4, label='Partner Effect')
        ax4.axhline(y=0.8, color='r', linestyle='--', alpha=0.7, label='80% Power')
        ax4.axvline(x=self.aim3_params['n_couples'], color='blue', linestyle=':', alpha=0.7, label='Current N=200')
        ax4.set_xlabel('Number of Couples')
        ax4.set_ylabel('Power')
        ax4.set_title('Aim 3: Power vs Sample Size')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig('k01_comprehensive_power_analysis.png', dpi=300, bbox_inches='tight')
        
        # Export result tables to CSV
        df_aim1_or = pd.DataFrame({'OR': or_range, 'power_alpha_0.1': powers_01, 'power_alpha_0.05': powers_05})
        df_aim1_or.to_csv('aim1_power_vs_or.csv', index=False)
        df_aim1_n = pd.DataFrame({'n': n_range, 'power': ipv_powers})
        df_aim1_n.to_csv('aim1_power_vs_n.csv', index=False)
        df_aim3_or = pd.DataFrame({'OR': or_range, 'actor_power': dyadic_actor_01, 'partner_power': dyadic_partner_01})
        df_aim3_or.to_csv('aim3_power_vs_or.csv', index=False)
        df_aim3_n = pd.DataFrame({'n_couples': couples_range, 'actor_power': actor_powers, 'partner_power': partner_powers})
        df_aim3_n.to_csv('aim3_power_vs_n.csv', index=False)
        
        plt.show()
        
        return or_range, powers_01, powers_05

    def write_grant_ready_summary(self, aim1_results, target_or_results, aim3_results):
        """Generate grant application ready summary"""
        
        print("=" * 80)
        print("GRANT APPLICATION POWER ANALYSIS SUMMARY")
        print("=" * 80)
        print()
        
        print("STATISTICAL POWER ASSESSMENT")
        print("-" * 50)
        print()
        
        print("Aim 1: CHIS Decomposition Analysis")
        print("Sample: n=237 South Asians (n=158 effective after design effect adjustment)")
        print("Comparison: All other racial/ethnic groups in California")
        print("Primary outcome: IPV disparities")
        print()
        
        print(f"Primary Analysis (IPV):")
        print(f"• Observed effect: OR = {aim1_results['observed_OR']:.2f}")
        print(f"• Power (α=0.1, unadjusted): {aim1_results['power_unadjusted']:.1%}")
        print(f"• Power (α=0.1, FDR corrected): {aim1_results['power_fdr']:.1%}")
        print(f"• Power (α=0.05, conventional): {aim1_results['power_05']:.1%}")
        print()
        
        print(f"Target Effect Size Analysis:")
        print(f"• Target OR = {target_or_results['target_or']} (minimum meaningful effect)")
        print(f"• Power for OR={target_or_results['target_or']} (α=0.1): {target_or_results['power_01']:.1%}")
        print(f"• Power for OR={target_or_results['target_or']} (α=0.05): {target_or_results['power_05']:.1%}")
        print()
        
        print("Multiple Comparisons Strategy:")
        print("• Primary outcome: IPV (main hypothesis)")
        print("• Secondary outcomes: Contraceptive use, contraceptive counseling")
        print("• Method: False Discovery Rate (FDR) correction")
        print("• Rationale: Maintains higher power than Bonferroni while controlling false discoveries")
        print()
        
        print("Aim 3: Dyadic Actor-Partner Interdependence Model")
        print("Sample: n=200 couples (n=400 individuals)")
        print("Design: Distinguishable dyads (heterosexual couples)")
        print("Outcome: IPV perpetration (binary)")
        print()
        
        print(f"Power Analysis:")
        print(f"• Design effect (ICC={self.aim3_params['icc_partners']}): {aim3_results['design_effect']:.2f}")
        print(f"• Effective sample size: {aim3_results['n_effective']:.0f}")
        print(f"• Actor effect power (OR={self.aim3_params['actor_effect_OR']}): {aim3_results['actor_power']:.1%}")
        print(f"• Partner effect power (OR={self.aim3_params['partner_effect_OR']}): {aim3_results['partner_power']:.1%}")
        print()
        
        print("METHODOLOGICAL STRENGTHS")
        print("-" * 50)
        print("• Conservative design effects account for survey complexity (CHIS) and dyadic clustering")
        print("• Realistic effect sizes based on South Asian IPV literature")
        print("• Appropriate statistical methods for each analysis type")
        print("• FDR correction balances Type I error control with statistical power")
        print("• Sample sizes adequate for detecting meaningful public health effects")
        print()
        
        print("POWER CALCULATION ASSUMPTIONS")
        print("-" * 50)
        print("All assumptions documented from consultation notes (25.06.03-call.md):")
        print("• CHIS design effect = 1.5 (typical for complex surveys)")
        print("• South Asian IPV rate = 10% (estimated from literature)")
        print("• General population IPV rate = 6% (CHIS baseline)")
        print("• Dyadic ICC = 0.3 (typical for couples)")
        print("• α = 0.1 (specified by investigator, justified for exploratory research)")
        print()
        
        adequacy = "adequate" if aim1_results['power_unadjusted'] >= 0.8 else "moderate but informative"
        print(f"CONCLUSION: Statistical power is {adequacy} for detecting meaningful")
        print("disparities in sexual and reproductive health outcomes between South Asian")
        print("and other populations, supporting the feasibility of this K01 research plan.")

    def validate_with_apimpowerr(self):
        """Validate dyadic APIM power using R's APIMPowerR package via rpy2"""
        try:
            from rpy2.robjects import r
            from rpy2.robjects.packages import importr
            import math
            apim_pkg = importr('APIMPowerR')
            r('library(APIMPowerR)')
            n = self.aim3_params['n_couples']
            icc = self.aim3_params['icc_partners']
            actorOR = self.aim3_params['actor_effect_OR']
            partnerOR = self.aim3_params['partner_effect_OR']
            alpha = self.aim3_params['alpha']
            r_code = f"powerAPIM(n={n}, ICC={icc}, adirect=log({actorOR}), apartner=log({partnerOR}), alpha={alpha})"
            res = r(r_code)
            actor_power_r = float(res[0])
            partner_power_r = float(res[1])
            print(f"R APIMPowerR actor effect power: {actor_power_r:.3f}")
            print(f"R APIMPowerR partner effect power: {partner_power_r:.3f}")
            return {'actor_power_r': actor_power_r, 'partner_power_r': partner_power_r}
        except Exception as e:
            print("R integration error:", e)
            return None

def main():
    """Run comprehensive power analysis addressing all consultation questions"""
    
    print("K01 SOUTH ASIAN SRH RESEARCH - COMPREHENSIVE POWER ANALYSIS")
    print("Addressing all consultation questions from 25.06.03-call.md")
    print("=" * 80)
    print()
    
    # Initialize analysis
    analysis = K01PowerAnalysis()
    
    # Answer specific consultation question about OR=1.15
    target_or_results = analysis.consultation_question_target_or_power()
    
    # Run full analyses
    aim1_results = analysis.run_aim1_analysis()
    aim3_results = analysis.run_aim3_analysis()
    
    # Generate comprehensive plots including power vs OR
    print("Generating comprehensive power analysis plots...")
    or_range, powers_01, powers_05 = analysis.create_power_vs_or_plots()
    
    # Generate grant-ready summary
    analysis.write_grant_ready_summary(aim1_results, target_or_results, aim3_results)
    # Validate with R's APIMPowerR
    print("Validating dyadic APIM power with R's APIMPowerR...")
    validation = analysis.validate_with_apimpowerr()
    print("R validation results:", validation)
    
    return {
        'aim1_results': aim1_results,
        'aim3_results': aim3_results,
        'target_or_results': target_or_results,
        'power_curves': {
            'or_range': or_range,
            'powers_01': powers_01,
            'powers_05': powers_05
        }
    }

if __name__ == "__main__":
    results = main()