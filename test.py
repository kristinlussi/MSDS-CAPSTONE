import json
import os
import re
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from main import *
import matplotlib.pyplot as plt

def main_test(expiring_pdf, renewal_pdf, threshold=0.95):
    html_parts = []
    html_parts.append("<html><head><meta charset='UTF-8'><title>Policy Diff - Entire Policy</title>")
    html_parts.append("""
    <style>
    body { font-family: Calibri, sans-serif; }
    table.diff {font-family:Courier; border:medium;}
    .diff_header {background-color:#e0e0e0}
    .diff_next {background-color:#c0c0c0}
    .diff_add {background-color:#aaffaa}
    .diff_chg {background-color:#ffff77}
    .diff_sub {background-color:#ffaaaa}
    pre { background-color: #f4f4f4; padding: 10px; }
    </style>
    """)
    html_parts.append("</head><body>")
    html_parts.append("<h1>Expiring vs. Renewal Policy Comparison Report</h1>")

    # Step 1: Extract text
    expiring_text = extract_ocr_text_from_pdf(expiring_pdf)
    renewal_text = extract_ocr_text_from_pdf(renewal_pdf)

    # Step 2: Clean and split
    expiring_paragraphs = smart_split_into_paragraphs(clean_text_for_comparison(expiring_text))
    renewal_paragraphs = smart_split_into_paragraphs(clean_text_for_comparison(renewal_text))

    html_parts.append(f"<p>Number of paragraphs in Expiring Policy: {len(expiring_paragraphs)}</p>")
    html_parts.append(f"<p>Number of paragraphs in Renewal Policy: {len(renewal_paragraphs)}</p>")

    # Step 3: Compare using embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    exp_embeddings = model.encode(expiring_paragraphs)
    ren_embeddings = model.encode(renewal_paragraphs)
    similarity_matrix = cosine_similarity(exp_embeddings, ren_embeddings)

    paragraph_predictions = []

    for i, exp_para in enumerate(expiring_paragraphs):
        # Find best match
        j = np.argmax(similarity_matrix[i])
        max_sim = similarity_matrix[i][j]
        ren_para = renewal_paragraphs[j]

        is_changed = max_sim < threshold
        paragraph_predictions.append(is_changed)

        if is_changed:
            diff_html = get_html_diff(exp_para, ren_para, context=False)
            html_parts.append(wrap_in_div(diff_html, f"Paragraph {i+1} - Possible Change (Similarity: {max_sim:.2f})"))
            html_parts.append("<hr>")

    html_parts.append("</body></html>")
    output_html = "\n".join(html_parts)

    print("Running...")

    return paragraph_predictions  # Return list of bools per paragraph

def strip_date_from_filename(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'\s*@\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', '', name)
    return name.strip()

def batch_test(expiring_dir, renewal_dir, groundtruth_dir):
    y_true = []
    y_pred = []

    for filename in os.listdir(expiring_dir):
        if not filename.endswith(".pdf"):
            continue

        policy_name = strip_date_from_filename(filename)
        expiring_pdf = os.path.join(expiring_dir, filename)

        # Match renewal
        matching_renewal_pdf = None
        for ren_file in os.listdir(renewal_dir):
            if ren_file.endswith(".pdf") and strip_date_from_filename(ren_file) == policy_name:
                matching_renewal_pdf = os.path.join(renewal_dir, ren_file)
                break

        groundtruth_file = os.path.join(groundtruth_dir, policy_name + ".json")

        if not matching_renewal_pdf or not os.path.exists(groundtruth_file):
            print(f"Skipping {policy_name}: missing renewal or annotation.")
            continue

        # Load ground truth
        with open(groundtruth_file, 'r') as f:
            truth = json.load(f)
        expected_changes = truth.get("paragraph_changes", [])

        # Get model predictions
        detected_changes = main_test(expiring_pdf, matching_renewal_pdf)
        # Ensure list
        if not isinstance(detected_changes, list):
            print(f"⚠️ Model output for {policy_name} is not a list.")
            continue

        # Sanity check length match
        if len(expected_changes) != len(detected_changes):
            print(f"⚠️ Mismatch in paragraph count for {policy_name}: expected {len(expected_changes)}, got {len(detected_changes)}")
            continue

        y_true.extend(expected_changes)
        y_pred.extend(detected_changes)

    if not y_true:
        print("No data processed. Check JSONs and model output.")
        return

    print(f"\nParagraph-level Evaluation ({len(y_true)} comparisons):\n")
    print(f"Accuracy:  {accuracy_score(y_true, y_pred):.4f}")
    print(f"Precision: {precision_score(y_true, y_pred):.4f}")
    print(f"Recall:    {recall_score(y_true, y_pred):.4f}")
    print(f"F1 Score:  {f1_score(y_true, y_pred):.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_true, y_pred, target_names=["Unchanged", "Changed"]))

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[False, True])  # False = Unchanged, True = Changed
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Unchanged", "Changed"])

    plt.figure(figsize=(6, 5))
    disp.plot(cmap="Blues", values_format='d')
    plt.title("Confusion Matrix: Paragraph-Level Classification")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    expiring_dir = "/Users/kristinlussi/Documents/GitHub/DATA698/ANNOTATED-POLICIES/EXPIRING"
    renewal_dir = "/Users/kristinlussi/Documents/GitHub/DATA698/ANNOTATED-POLICIES/RENEWAL"
    groundtruth_dir = "/Users/kristinlussi/Documents/GitHub/DATA698/ANNOTATED-POLICIES/ANNOTATIONS"
    batch_test(expiring_dir, renewal_dir, groundtruth_dir)