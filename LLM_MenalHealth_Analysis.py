#Intial pipeline for analysis

from scipy.stats import f_oneway
import numpy as np

# Sample data for your three groups
llm_fttc = [85, 88, 92, 89, 95]
general_llm = [78, 80, 75, 83, 79]
none_group = [65, 68, 70, 62, 66]

# Perform the one-way ANOVA
f_statistic, p_value = f_oneway(llm_fttc, general_llm, none_group)

print(f"F-statistic: {f_statistic}")
print(f"P-value: {p_value}")

# Interpret the results
alpha = 0.05
if p_value < alpha:
    print("Result: Reject the null hypothesis. There is a significant difference among the group means.")
else:
    print("Result: Fail to reject the null hypothesis. There is no significant difference among the group means.")

# If the above rejects null then this to ID which groups differentiated
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Assume 'data' is the DataFrame from the previous example
data = pd.DataFrame({
    'score': [85, 88, 92, 89, 95, 78, 80, 75, 83, 79, 65, 68, 70, 62, 66],
    'group': ['LLM FTTC'] * 5 + ['General LLM'] * 5 + ['None'] * 5
})

# Perform Tukey's HSD post-hoc test
tukey_result = pairwise_tukeyhsd(endog=data['score'], groups=data['group'], alpha=0.05)

print(tukey_result)