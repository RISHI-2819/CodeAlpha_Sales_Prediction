import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 200

tv = np.round(np.random.uniform(5.0, 300.0, n_samples), 1)
radio = np.round(np.random.uniform(0.0, 50.0, n_samples), 1)
newspaper = np.round(np.random.exponential(scale=25.0, size=n_samples), 1)
newspaper = np.clip(newspaper, 0.3, 114.0)

# True relationship with realistic noise and interaction effect
sales = (
    3.0 
    + 0.046 * tv 
    + 0.185 * radio 
    + 0.003 * newspaper 
    + 0.0009 * (tv * radio) 
    + np.random.normal(0, 1.4, size=n_samples)
)
sales = np.round(np.clip(sales, 1.6, 32.0), 1)

df = pd.DataFrame({
    'TV': tv,
    'Radio': radio,
    'Newspaper': newspaper,
    'Sales': sales
})

df.to_csv('advertising.csv', index=False)
print("advertising.csv created successfully with shape:", df.shape)
