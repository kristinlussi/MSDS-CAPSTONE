import matplotlib.pyplot as plt
from test import *

# Metrics for Changed and Unchanged labels
labels = ["Unchanged", "Changed"]
precision = [0.88, 0.738]
recall = [0.94, 0.583]
f1_score = [0.91, 0.651]

# Plotting
x = range(len(labels))
width = 0.25

plt.figure(figsize=(10, 6))
plt.bar([p - width for p in x], precision, width=width, label="Precision")
plt.bar(x, recall, width=width, label="Recall")
plt.bar([p + width for p in x], f1_score, width=width, label="F1 Score")

plt.xticks(x, labels)
plt.ylim(0, 1.1)
plt.ylabel("Score")
plt.title("Paragraph-Level Classification Metrics by Label")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

plt.show()
