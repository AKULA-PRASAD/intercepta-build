# INTERCEPTA AUDIT ACTION PLAN
# Every issue found must be fixed before building more

## PARAMETER FIXES (5 assumed parameters)
1. alpha_r=0.4: sensitivity analysis needed
2. Emax 0.18 in vivo correction: find published PD ratios
3. Escape transition rates: Beltran 2016 time-course data
4. g_mod_N=1.3: literature NE vs adenocarcinoma Ki67
5. frac_N=0.03: Beltran 2016 histology frequencies

## CLAIM FIXES (5 inflated claims)
1. "Novel molecule generation" → rename "scaffold hopping"
2. "13 better than alisertib" → already corrected
3. "Zero tuned parameters" → fix to "1 assumed, 4 derived"
4. Scout 4 → already redefined as data-driven
5. p38 MAPK → compute proper FDR-corrected statistics

## PRIORITY ORDER
1. p38 MAPK statistics (validates AML finding)
2. alpha_r sensitivity analysis (validates ODE claim)
3. AML ODE with published parameters
4. Remaining parameter fixes
