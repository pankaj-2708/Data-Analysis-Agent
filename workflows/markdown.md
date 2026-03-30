# **Iris Flower Dataset Analysis Report**

This report provides a comprehensive analysis of the Iris Flower dataset, which consists of 150 samples with 6 columns, including 4 numerical measurements and 1 categorical variable representing species. The dataset is well-balanced, with 50 samples for each of the three species: *Iris-setosa*, *Iris-versicolor*, and *Iris-virginica*.

---

## **Dataset Overview**

### File Metadata
| **Property**       | **Value** |
|-------------------|-----------|
| Total Rows        | 150       |
| Total Columns     | 6         |
| Duplicate Rows    | 0         |


### Columns Description

| **Column Name**     | **Data Type** | **Semantic Type** | **Description**                          | **Null Count** | **Unique Values** |
|---------------------|---------------|-------------------|------------------------------------------|----------------|-------------------|
| Id                  | int64         | identifier        | Unique identifier for each row.           | 0              | 150               |
| SepalLengthCm       | float64       | numeric_metric    | Sepal length in cm.                      | 0              | 35                |
| SepalWidthCm        | float64       | numeric_metric    | Sepal width in cm.                       | 0              | 23                |
| PetalLengthCm       | float64       | numeric_metric    | Petal length in cm.                      | 0              | 43                |
| PetalWidthCm        | float64       | numeric_metric    | Petal width in cm.                       | 0              | 22                |
| Species             | object        | categorical       | Species of the iris flower.               | 0              | 3                 |


---

## **Key Statistics**

### Summary Statistics for Numerical Columns

| **Metric**  | **SepalLengthCm** | **SepalWidthCm** | **PetalLengthCm** | **PetalWidthCm** |
|-------------|--------------------|-------------------|--------------------|-------------------|
| Count       | 150.0              | 150.0             | 150.0              | 150.0             |
| Mean        | 5.84               | 3.05              | 3.76               | 1.20              |
| Std         | 0.83               | 0.43              | 1.76               | 0.76              |
| Min         | 4.3                | 2.0               | 1.0                | 0.1               |
| 25%         | 5.1                | 2.8               | 1.6                | 0.3               |
| 50%         | 5.80               | 3.00              | 4.35               | 1.30              |
| 75%         | 6.4                | 3.3               | 5.1                | 1.8               |
| Max         | 7.9                | 4.4               | 6.9                | 2.5               |

---

### Frequency Distribution of Species

The dataset is perfectly balanced, with each species contributing exactly 33.33% to the total samples.


| **Species**        | **Percentage** |
|--------------------|----------------|
| setosa             | 33.33%         |
| versicolor         | 33.33%         |
| virginica          | 33.33%         |



![Species Distribution](../data/species_count.png)

---

### Correlation Matrix for Numerical Columns

The correlation matrix reveals strong positive correlations between petal dimensions (`petal_length` and `petal_width`) and sepal length (`sepal_length`). Sepal width exhibits weak negative correlations with other features.



| **Feature**         | **SepalLengthCm** | **SepalWidthCm** | **PetalLengthCm** | **PetalWidthCm** |
|---------------------|--------------------|-------------------|--------------------|-------------------|
| **SepalLengthCm**   | 1.00               | -0.11              | 0.87               | 0.82              |
| **SepalWidthCm**    | -0.11              | 1.00              | -0.42              | -0.36             |
| **PetalLengthCm**   | 0.87               | -0.42             | 1.00               | 0.96              |
| **PetalWidthCm**    | 0.82               | -0.36             | 0.96               | 1.00              |



![Feature Correlation Heatmap](../data/feature_correlation_heatmap.png)


---

### Grouped Statistics by Species

#### Mean, Median, and Std of Numerical Columns Grouped by Species

| **Species**    | **Sepal Length (Mean)** | **Sepal Width (Mean)** | **Petal Length (Mean)** | **Petal Width (Mean)** |
|----------------|-------------------------|------------------------|-------------------------|------------------------|
| setosa        | 5.01                    | 3.42                   | 1.46                    | 0.24                   |
| versicolor    | 5.94                    | 2.77                   | 4.26                    | 1.33                   |
| virginica     | 6.59                    | 2.97                   | 5.55                    | 2.03                   |


---

### Outlier Detection Using IQR Method

The following bounds identify potential outliers in the numerical columns:


| **Feature**         | **Lower Bound** | **Upper Bound** |
|---------------------|-----------------|-----------------|
| SepalLengthCm       | 3.15            | 8.35            |
| SepalWidthCm        | 2.05            | 4.05            |
| PetalLengthCm       | -3.65           | 10.35           |
| PetalWidthCm        | -1.95           | 4.05            |


---

### Distribution Metrics

#### Skewness and Kurtosis

| **Feature**         | **Skewness**    | **Kurtosis**     |
|---------------------|-------------------|-------------------|
| SepalLengthCm       | 0.31              | -0.55             |
| SepalWidthCm        | 0.33              | 0.29              |
| PetalLengthCm       | -0.27             | -1.40             |
| PetalWidthCm        | -0.10             | -1.34             |


#### Range (Max - Min)

| **Feature**         | **Range** |
|---------------------|-----------|
| SepalLengthCm       | 3.6       |
| SepalWidthCm        | 2.4       |
| PetalLengthCm       | 5.9       |
| PetalWidthCm        | 2.4       |


#### Coefficient of Variation

| **Feature**         | **Coefficient of Variation** |
|---------------------|-----------------------------|
| SepalLengthCm       | 0.14                         |
| SepalWidthCm        | 0.14                         |
| PetalLengthCm       | 0.47                         |
| PetalWidthCm        | 0.64                         |


#### Percentiles

| **Feature**         | **10th Percentile** | **25th Percentile** | **50th Percentile** | **75th Percentile** | **90th Percentile** |
|---------------------|---------------------|---------------------|---------------------|---------------------|---------------------|
| SepalLengthCm       | 4.8                 | 5.1                 | 5.80                | 6.4                 | 6.90                |
| SepalWidthCm        | 2.5                 | 2.8                 | 3.00                | 3.3                 | 3.61                |
| PetalLengthCm       | 1.4                 | 1.6                 | 4.35                | 5.1                 | 5.80                |
| PetalWidthCm        | 0.2                 | 0.3                 | 1.30                | 1.8                 | 2.20                |


---

## **Visual Insights**


### Distribution of Sepal Length by Species

![Sepal Length Distribution](../data/sepal_length_distribution.png)

*Sepal length distributions are distinct across species, with *Iris-setosa* showing a lower range (4.3�5.8 cm) compared to *Iris-versicolor* and *Iris-virginica* (5.1�6.9 cm).*



---

### Distribution of Sepal Width by Species

![Sepal Width Distribution](../data/sepal_width_distribution.png)

*Sepal width distributions overlap significantly across species, though *Iris-setosa* shows a slightly higher mean width (3.42 cm) compared to others.*



---

### Distribution of Petal Length by Species

![Petal Length Distribution](../data/petal_length_distribution.png)

*Petal length exhibits the strongest differentiation between species. *Iris-setosa* has significantly shorter petals (1.0�1.9 cm) compared to *Iris-versicolor* (3.0�5.1 cm) and *Iris-virginica* (4.5�6.9 cm).*


---

### Distribution of Petal Width by Species

![Petal Width Distribution](../data/petal_width_distribution.png)

*Petal width distributions are also highly species-specific. *Iris-setosa* petals are distinctly narrower (0.1�0.6 cm), while *Iris-versicolor* and *Iris-virginica* show wider ranges.*


---

### Box Plot Comparison Across Species

![Numeric vs Species Box Plot](../data/numeric_vs_species_box.png)

*This box plot compares the distributions of sepal and petal measurements across species. Key observations:*

- *Median sepal length and width are highest in *Iris-virginica*.*
- *Petal length and width distributions for *Iris-setosa* do not overlap with other species, confirming its distinct morphological traits.*
- *Outliers are present but relatively few, indicating most measurements cluster tightly around the median.*



---

### Scatter Plot: Sepal Length vs. Sepal Width


![Sepal Comparison Scatter Plot](../data/sepal_compared_scatter.png)

*Sepal measurements overlap significantly across *Iris-versicolor* and *Iris-virginica*, but *Iris-setosa* forms a distinct cluster with lower sepal length and higher width.*



---

### Scatter Plot: Petal Length vs. Petal Width


![Petal Comparison Scatter Plot](../data/petal_compared_scatter.png)
*This plot clearly separates the three species based on petal dimensions. *Iris-setosa* has short, narrow petals, while *Iris-virginica* has long, wide petals. *Iris-versicolor* occupies the middle ground.*



---

### Scatter Plot: Sepal Length vs. Petal Length


![Sepal vs Petal Scatter Plot](../data/sepal_vs_petal_scatter.png)
*The strong positive relationship between sepal and petal length (correlation = 0.87) is evident. *Iris-setosa* stands apart with shorter petals relative to its sepal length.*



---

### Pair Plot (Scatter Matrix)


![Pair Plot](../data/pair_plot.png)

*This matrix provides a holistic view of feature relationships. Key insights include:*
- *Strong linear relationships between petal dimensions and sepal length.*
- *Clear clustering of *Iris-setosa* in the lower-left quadrant, indicating smaller petals and sepals.*
- *Overlap between *Iris-versicolor* and *Iris-virginica* in feature space but still distinguishable.*



---

### Violin Plot: Feature Distribution by Species


![Species Distribution by Feature](../data/species_distribution_by_feature.png)

*Violin plots showcase the density and spread of measurements per species:*
- *Sepal width has the narrowest distribution, particularly in *Iris-setosa*.*
- *Petal length and width show bimodal distributions for *Iris-versicolor* and *Iris-virginica*, reflecting morphological variability within species.*
- *The wider bulges in violin plots indicate higher density around median values.*



---

## **Conclusion**


This analysis reveals that *Iris-setosa* is morphologically distinct from *Iris-versicolor* and *Iris-virginica*, particularly in petal dimensions. The strong correlations between sepal length and petal measurements suggest an underlying geometric relationship in iris flowers. The balanced dataset and lack of outliers ensure robustness in these findings. Future work could explore clustering algorithms to validate species groupings or apply predictive models to classify iris species based on measurements.
