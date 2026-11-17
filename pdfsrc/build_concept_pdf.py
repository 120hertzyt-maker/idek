#!/usr/bin/env python3
"""Concept-first ML notes (4 pages) built from the notebooks in this repo.

Structure: for each concept -> what / why / how / components / when /
limitations / confused-with / how our code implements it.
No saved-output memorisation: numbers appear only when they teach a formula.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether, CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJM", FD + "DejaVuSansMono.ttf"))
registerFontFamily("DJ", normal="DJ", bold="DJB", italic="DJ", boldItalic="DJB")

INK = colors.HexColor("#14213d")
NAVY = colors.HexColor("#1d3557")
ACC = colors.HexColor("#b23a48")
ACC2 = colors.HexColor("#2a6f97")
TEAL = colors.HexColor("#0b6e4f")
PURP = colors.HexColor("#5b3f8c")
GREY = colors.HexColor("#4a4e57")
BG = colors.HexColor("#eef2f7")
RULE = colors.HexColor("#c9d3df")

BODY = ParagraphStyle("body", fontName="DJ", fontSize=8.05, leading=9.95,
                      textColor=INK, spaceAfter=1.2)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.55, leading=9.4)
FORM = ParagraphStyle("form", fontName="DJM", fontSize=7.4, leading=9.4,
                      textColor=colors.HexColor("#16324f"), leftIndent=3,
                      backColor=BG, borderPadding=(1.6, 3, 1.6, 3),
                      spaceBefore=1.2, spaceAfter=1.6)
H1 = ParagraphStyle("h1", fontName="DJB", fontSize=9.6, leading=11.2,
                    textColor=colors.white)
H2 = ParagraphStyle("h2", fontName="DJB", fontSize=8.5, leading=10.2,
                    textColor=NAVY, spaceBefore=3.2, spaceAfter=0.6)
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=6.8, bulletIndent=1.4,
                     spaceAfter=1.0)
BULS = ParagraphStyle("buls", parent=SMALL, leftIndent=6.4, bulletIndent=1.2,
                      spaceAfter=0.8)

STORY = []
PEND = []


class Pend(object):
    def __init__(self, items):
        self.items = items


def A(x):
    if isinstance(x, Pend):
        PEND.extend(x.items)
        return
    if PEND:
        STORY.extend(PEND)
        del PEND[:]
    if isinstance(x, (list, tuple)):
        STORY.extend(x)
    else:
        STORY.append(x)


def P(t, s=BODY):
    return Paragraph(t, s)


def B(t):
    return Paragraph(t, BUL, bulletText="\u2022")


def S(t):
    return Paragraph(t, BULS, bulletText="\u2013")


def F(t):
    return Paragraph(t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                     .replace("\n", "<br/>"), FORM)


def H(t, color=NAVY):
    tbl = Table([[Paragraph(t, H1)]], colWidths=["100%"])
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color),
                             ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                             ("TOPPADDING", (0, 0), (-1, -1), 2.2),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6)]))
    return Pend([CondPageBreak(30 * mm), Spacer(1, 3.0), tbl, Spacer(1, 3.0)])


def h2(t):
    return Paragraph(t, H2)


def T(rows, widths, headbg=NAVY, fs=7.25, maxrows=None, zebra=True):
    th = ParagraphStyle("th", fontName="DJB", fontSize=fs, leading=fs + 1.7,
                        textColor=colors.white)
    td = ParagraphStyle("td", fontName="DJ", fontSize=fs, leading=fs + 1.9,
                        textColor=INK)
    data = [[Paragraph(c, th) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(c, td) for c in r])

    def build(chunk):
        t = Table([data[0]] + chunk, colWidths=widths, repeatRows=1)
        st = [("BACKGROUND", (0, 0), (-1, 0), headbg),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("LEFTPADDING", (0, 0), (-1, -1), 3.0),
              ("RIGHTPADDING", (0, 0), (-1, -1), 2.6),
              ("TOPPADDING", (0, 0), (-1, -1), 1.6),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 1.9),
              ("GRID", (0, 0), (-1, -1), 0.3, RULE)]
        if zebra:
            for i in range(1, len(chunk) + 1):
                if i % 2 == 0:
                    st.append(("BACKGROUND", (0, i), (-1, i),
                               colors.HexColor("#f2f5f9")))
        t.setStyle(TableStyle(st))
        return t

    body = data[1:]
    head = list(PEND)
    del PEND[:]
    if maxrows is None:
        # let ReportLab split it; repeatRows=1 re-draws the header on the next column
        return head + [build(body)]
    chunks = [body[i:i + maxrows] for i in range(0, len(body), maxrows)]
    if len(chunks) == 1:
        return (head + [build(chunks[0])]) if head else [build(chunks[0])]
    out = []
    for i, ch in enumerate(chunks):
        blk = build(ch)
        out.append(KeepTogether(head + [blk]) if (i == 0 and head)
                   else KeepTogether([blk]))
    return out


PW, PH = A4
LM = RM = 12.0 * mm
TM = 11.0 * mm
BM = 9.5 * mm
GUT = 6.0 * mm
COLW = (PW - LM - RM - GUT) / 2.0

# ============================== PAGE 1 =====================================
banner = Table([[Paragraph("Machine Learning &mdash; Concept Notes",
                           ParagraphStyle("bt", fontName="DJB", fontSize=12.2,
                                          leading=14, textColor=colors.white))],
                [Paragraph("What each algorithm is, why it exists, how it works, "
                           "and what the code does. Built from the lab programs.",
                           ParagraphStyle("bs", fontName="DJ", fontSize=7.0,
                                          leading=8.8,
                                          textColor=colors.HexColor("#cbd8e8")))]],
               colWidths=[COLW])
banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, 0), 4.5),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
                            ("TOPPADDING", (0, 1), (-1, 1), 0),
                            ("BOTTOMPADDING", (0, 1), (-1, 1), 5)]))
A(banner)
A(Spacer(1, 2.5))
A(P("The goal is <b>generalisation</b> &mdash; doing well on data never seen in training. A model at 100% train / 70% "
    "test has memorised, not learned. Every notebook follows: clean &rarr; EDA &rarr; split &rarr; scale (fit on train "
    "only) &rarr; fit &rarr; predict &rarr; evaluate &rarr; tune by CV &rarr; report once on the untouched test set.", SMALL))

# ---------------------------------------------------------------- 0 --------
A(H("0 &middot; The frame everything sits in", GREY))
A(P("<b>Supervised learning</b> learns a mapping from inputs (features <font face='DJM'>X</font>) to a known "
    "target (<font face='DJM'>y</font>). If <font face='DJM'>y</font> is a category &rarr; <b>classification</b>; if "
    "continuous &rarr; <b>regression</b>. <b>Unsupervised</b> learning has no <font face='DJM'>y</font> and looks for "
    "structure (clustering, dimensionality reduction). Every lab here except EDA is supervised classification."))
A(T([
    ["Term", "Meaning, and the fix"],
    ["Overfitting", "Fits noise/quirks of the training set; high variance. Fix: simpler model, more data, "
     "regularisation, pruning, dropout, early stopping."],
    ["Underfitting", "Too simple to capture the pattern; high bias. Fix: more capacity, better features, "
     "less regularisation."],
    ["Bias / variance", "Bias = error from wrong assumptions (consistently off). Variance = sensitivity to "
     "the particular training sample. Total error &asymp; bias&sup2; + variance + noise."],
    ["Leakage", "Information from test data influencing training (e.g. scaling before splitting, tuning on "
     "test). Fix: fit every transformer on train only."],
], [COLW * 0.26, COLW * 0.74], headbg=GREY, fs=7.1))
A(Spacer(1, 1.6))

# ---------------------------------------------------------------- 1 --------
A(H("1 &middot; Decision Trees", ACC2))
A(P("<b>What:</b> a flowchart model. Each <b>internal node</b> tests one feature against a threshold, each "
    "<b>branch</b> is an outcome, each <b>leaf</b> stores a prediction &mdash; the majority class (classification) "
    "or mean target (regression). Prediction = route one sample from the <b>root</b> down to a leaf."))
A(P("<b>Why:</b> human-readable, needs no feature scaling, handles non-linear interactions and mixed data, "
    "and gives <b>feature importance</b>. <b>Limits:</b> unstable (a small data change can rebuild the tree), "
    "splits are axis-aligned so diagonal boundaries become staircases, and a fully grown tree overfits."))
A(P("<b>How it learns</b> &mdash; greedy recursive binary splitting:"))
A(F("1. at a node, try every feature and every mid-point threshold\n"
    "2. score each candidate split by the impurity drop it produces\n"
    "3. keep the best (lowest weighted child impurity) and recurse\n"
    "4. stop at max_depth / min_samples_* / pure node -> make a leaf"))
A(P("Impurity measures how mixed a node's classes are (0 = pure):"))
A(F("Gini(p)    = 1 - sum_k p_k^2\n"
    "Entropy(p) = -sum_k p_k * log2(p_k)\n"
    "InfoGain   = H(parent) - sum_c (n_c / n) * H(child_c)"))
A(P("Gini and entropy usually pick similar trees; gini is cheaper (no log). Neither is 'better' in general &mdash; "
    "that is why labs test both."))
A(T([
    ["Component", "What it actually controls"],
    ["<font face='DJM'>criterion</font>", "gini or entropy &mdash; the split-scoring function."],
    ["<font face='DJM'>max_depth</font>", "Maximum root-to-leaf length. Small = simpler, less overfit (pre-pruning)."],
    ["<font face='DJM'>min_samples_split</font> / <font face='DJM'>_leaf</font>", "A node needs this many samples to split / a leaf must keep this many."],
    ["<font face='DJM'>max_features</font>", "How many features are considered per split (randomness)."],
    ["<font face='DJM'>ccp_alpha</font>", "Cost-complexity pruning strength: penalises leaf count, applied <i>after</i> growing (post-pruning). &alpha;=0 keeps the full tree."],
    ["<font face='DJM'>random_state</font>", "Fixes tie-breaking/reproducibility &mdash; not model quality."],
], [COLW * 0.30, COLW * 0.70], headbg=ACC2, fs=7.1))
A(Spacer(1, 1.4))
A(P("<b>Pruning, two ways:</b> <b>pre-pruning</b> stops growth early (depth, leaf size); <b>post-pruning</b> grows "
    "fully then cuts back branches that do not pay for their complexity. "
    "<font face='DJM'>cost_complexity_pruning_path()</font> returns the candidate &alpha; values and the matching "
    "impurities, so you can sweep &alpha; instead of guessing."))
A(P("<b>In our program:</b> split the breast-cancer features, fit a default tree, then compare <font face='DJM'>gini</font> "
    "vs <font face='DJM'>entropy</font>, sweep <font face='DJM'>max_depth</font>, prune with "
    "<font face='DJM'>ccp_alpha</font> from the pruning path, and read <font face='DJM'>feature_importances_</font> "
    "and <font face='DJM'>plot_tree</font> for interpretation. <font face='DJM'>get_depth()</font> / "
    "<font face='DJM'>get_n_leaves()</font> describe the fitted tree; <font face='DJM'>predict_proba()</font> returns "
    "the class mix in the reached leaf."))

# ---------------------------------------------------------------- 2 --------
A(H("2 &middot; K-Nearest Neighbours", TEAL))
A(P("<b>What:</b> a <i>lazy, instance-based</i> classifier. There is no training phase &mdash; "
    "<font face='DJM'>fit()</font> just stores the data. Prediction measures the Euclidean distance "
    "<font face='DJM'>d = sqrt(&Sigma;(x_i &minus; z_i)&sup2;)</font> from the query to every training point, takes the "
    "<b>k</b> closest and votes (for regression, averages their targets)."))
A(P("<b>Why:</b> no assumptions about the shape of the boundary, trivially simple. <b>Limits:</b> prediction is "
    "slow (compares against everything), memory heavy, dies in high dimensions (<b>curse of dimensionality</b> &mdash; "
    "distances concentrate and 'nearest' stops meaning much), and it is extremely sensitive to feature scale."))

A(T([
    ["Knob", "Effect"],
    ["<font face='DJM'>n_neighbors</font>", "Small k = flexible, low bias, high variance (noise wins). Large k = smooth, "
     "high bias (boundary blurs). Default 5."],
    ["<font face='DJM'>weights</font>", "<font face='DJM'>'uniform'</font> = one vote each; <font face='DJM'>'distance'</font> = closer neighbours count more."],
    ["<font face='DJM'>metric</font> / <font face='DJM'>p</font>", "Distance definition; <font face='DJM'>p=2</font> Euclidean, <font face='DJM'>p=1</font> Manhattan."],
    ["Scaling", "Mandatory: a feature in the thousands otherwise dominates the distance."],
], [COLW * 0.24, COLW * 0.76], headbg=TEAL, fs=7.1))
A(P("<b>Confused with:</b> K-Means (an <i>unsupervised clustering</i> algorithm that also uses k, but finds centroids "
    "and has nothing to do with labels); k in KNN = neighbours, k in K-Means = clusters."))
A(P("<b>In our program:</b> a <font face='DJM'>Pipeline</font> of <font face='DJM'>StandardScaler</font> &rarr; "
    "<font face='DJM'>SelectKBest(f_classif)</font> &rarr; <font face='DJM'>KNeighborsClassifier</font>, tuned with a "
    "manual loop and <font face='DJM'>RandomizedSearchCV</font> over k, weights and metric, scored by cross-validated "
    "AUC. The scaling step is the reason KNN becomes competitive here."))

# ---------------------------------------------------------------- 3 --------
A(H("3 &middot; Evaluating a classifier", PURP))
A(P("<b>The confusion matrix</b> is the source of every metric. Rows = actual, columns = predicted:"))
A(F("                 pred 0    pred 1\n"
    "   actual 0      TN        FP\n"
    "   actual 1      FN        TP"))
A(P("TP/FP/FN/TN are defined with respect to the <b>positive class</b> (usually 1), so swapping which class is "
    "'positive' swaps precision and recall."))
A(F("accuracy  = (TP+TN) / N          # misleading when classes are imbalanced\n"
    "precision = TP / (TP+FP)          # of the ones I flagged, how many were right\n"
    "recall    = TP / (TP+FN)          # of the real positives, how many I caught\n"
    "F1        = 2*P*R / (P+R)         # harmonic mean, punishes imbalance between P and R"))
A(P("<b>Macro</b> averages per-class scores equally (a rare class matters as much as a common one); "
    "<b>weighted</b> averages by class support (≈ accuracy's bias). Use macro when rare classes matter."))
A(P("<b>ROC/AUC</b> sweeps the threshold (TPR vs FPR); AUC = chance a random positive is ranked above a random "
    "negative, so it measures <i>ranking</i> and needs scores, not just labels."))
A(P("<b>Cross-validation:</b> split the training data into k folds, train on k&minus;1 and validate on the held-out "
    "fold, k times; average the score. It gives a lower-variance estimate than one split and lets every point be "
    "validated once. <b>StratifiedKFold</b> keeps each fold's class proportions &mdash; essential for imbalanced data. "
    "The test set stays untouched until the very end."))
A(P("<b>Why accuracy is not enough:</b> with 95% negatives, predicting 'negative' always scores 95% accuracy while "
    "catching zero positives. Balanced accuracy averages recall per class; F1 ignores true negatives entirely."))
A(P("<b>In our program:</b> <font face='DJM'>classification_report</font>, <font face='DJM'>confusion_matrix</font>, "
    "row-normalised matrices to see <i>where</i> errors go, <font face='DJM'>roc_auc_score</font> for tuning, and "
    "<font face='DJM'>cross_val_score</font> inside the searches."))

# ============================== PAGE 2 =====================================
A(H("4 &middot; Naive Bayes and text data", NAVY))
A(P("<b>Bayes' theorem</b> turns a prior belief into a posterior after seeing evidence:"))
A(F("P(c | x) = P(x | c) * P(c) / P(x)\n"
    " posterior   likelihood  prior   evidence"))
A(P("Predict the largest posterior; <b>P(x)</b> is identical for all classes, so it can be dropped. "
    "<b>Why 'naive':</b> features are assumed conditionally independent given the class, so "
    "<font face='DJM'>P(x|c) = &prod; P(x_i|c)</font>. That is almost always false (words correlate), yet the "
    "<i>argmax</i> usually survives &mdash; it only needs the right class to win. Consequence: the scores are "
    "<b>overconfident</b> and not usable as calibrated probabilities."))
A(P("<b>Why logs:</b> multiplying hundreds of small probabilities underflows to 0.0 in floating point; summing logs is "
    "numerically stable and mathematically identical (monotone transform, so argmax is unchanged)."))
A(F("log P(c|x) = log P(c) + sum_i log P(x_i | c)   (+ const)"))
A(P("<b>Laplace / additive smoothing</b> &mdash; an unseen word gives count 0, so the whole product becomes 0 and that "
    "class is permanently vetoed. Add &alpha; to every count:"))
A(F("P(word | class) = (count(word, class) + alpha)\n"
    "                  / (total_words_in_class + alpha * V)\n"
    "V = vocabulary size; alpha*V keeps the distribution summing to 1"))
A(P("&alpha; &rarr; 0 trusts the data (overfits, vetoes unseen words); &alpha; &rarr; large flattens every class toward "
    "uniform (underfits). &alpha; is tuned on a <i>validation</i> split, never on test."))
A(T([
    ["Variant", "Assumes / used for"],
    ["<font face='DJM'>MultinomialNB</font>", "Feature counts (word frequencies). The text default."],
    ["<font face='DJM'>GaussianNB</font>", "Continuous features, each class-conditional feature ~ Normal(&mu;,&sigma;&sup2;)."],
    ["<font face='DJM'>BernoulliNB</font>", "Binary presence/absence of each feature."],
    ["<font face='DJM'>CategoricalNB</font>", "Categorical (non-numeric) features."],
], [COLW * 0.30, COLW * 0.70], headbg=NAVY, fs=7.1))
A(Spacer(1, 1.4))
A(P("<b>Text pipeline:</b> raw text &rarr; tokenise &rarr; lowercase/strip accents/remove stop-words &rarr; build a "
    "vocabulary &rarr; vectorise into a matrix (rows = documents, columns = terms) &rarr; weight &rarr; classifier."))
A(T([
    ["Component", "What it does"],
    ["<font face='DJM'>CountVectorizer</font>", "Bag-of-words: counts occurrences, ignores word order. "
     "<font face='DJM'>ngram_range=(1,2)</font> also counts adjacent pairs; <font face='DJM'>min_df=2</font> drops terms "
     "seen in fewer than 2 documents; <font face='DJM'>stop_words</font> removes very common words."],
    ["<font face='DJM'>TfidfVectorizer</font>", "Counts, then weights each term by how <i>rare</i> it is across documents."],
    ["<font face='DJM'>fit</font>", "Learns the vocabulary / document frequencies from the data."],
    ["<font face='DJM'>transform</font>", "Applies that learned vocabulary to new text (no relearning)."],
    ["<font face='DJM'>fit_transform</font>", "Both, in one call &mdash; train only. Using it on test leaks the vocabulary."],
], [COLW * 0.30, COLW * 0.70], headbg=NAVY, fs=7.1))
A(Spacer(1, 1.4))
A(F("tf-idf(t, d) = tf(t, d) * idf(t)\n"
    "idf(t)       = log((1 + n) / (1 + df(t))) + 1\n"
    "then each row is L2-normalised:  x / ||x||_2"))
A(P("<b>tf</b> rewards a term appearing in this document; <b>idf</b> punishes terms appearing everywhere. Raw counts "
    "let long documents and common words dominate; TF-IDF equalises both. With count data, NB's likelihood is a true "
    "multinomial; with TF-IDF the values are no longer counts, so the model's assumptions are only approximate &mdash; "
    "which is why an untuned TF-IDF NB can be <i>worse</i> than plain counts."))
A(P("<b>Confused with:</b> BernoulliNB (presence, not counts), and TF-IDF (a weighting scheme, not a model)."))
A(P("<b>In our program:</b> a custom NB written from the formulas above "
    "(<font face='DJM'>class_log_prior_</font>, <font face='DJM'>feature_log_prob_</font>, then "
    "<font face='DJM'>scores = X @ feature_log_prob_.T + class_log_prior_</font> and "
    "<font face='DJM'>argmax</font>), verified against <font face='DJM'>MultinomialNB</font>, then a "
    "<font face='DJM'>Pipeline(TfidfVectorizer &rarr; MultinomialNB)</font> tuned with a grid over "
    "<font face='DJM'>ngram_range</font> and <font face='DJM'>alpha</font> on a dev split."))

# ---------------------------------------------------------------- 5 --------
A(H("5 &middot; Support Vector Machines", ACC))
A(P("<b>What:</b> finds the hyperplane that separates the classes with the <b>widest margin</b> &mdash; the largest "
    "empty band around the boundary. <b>Support vectors</b> are the few points sitting on the margin's edge; they alone "
    "determine the boundary, so deleting other points changes nothing."))
A(F("margin = 2 / ||w||          ->  maximise margin = minimise ||w||\n"
    "hard margin : y_i (w.x_i + b) >= 1                 (no errors allowed)\n"
    "soft margin : min  1/2||w||^2 + C * sum_i xi_i      (slack xi_i >= 0)"))
A(P("<b>C is the inverse regularisation strength.</b> Small C = heavy regularisation, a wide soft margin that tolerates "
    "misclassified points (more bias, less variance). Large C = little regularisation, the model fights for every point, "
    "narrow margin, overfits outliers. C is a hyperparameter; <b>w</b> is learned."))
A(P("<b>Why maximise the margin:</b> the widest band is the most regularised, best-generalising boundary. "
    "<b>The kernel trick:</b> a linear separator in a high-dimensional space &phi;(x) is a curved boundary in the "
    "original space, and the optimisation only ever needs the inner product <font face='DJM'>K(x,x') = "
    "&phi;(x)&middot;&phi;(x')</font> &mdash; never &phi; itself, which may be infinite-dimensional."))
A(T([
    ["Kernel", "Boundary it can form", "Notes"],
    ["<font face='DJM'>'linear'</font>", "A straight hyperplane", "Use when data is (nearly) linearly separable or features &gt;&gt; samples."],
    ["<font face='DJM'>'poly'</font>", "Polynomial curves; <font face='DJM'>degree</font> sets the power", "Captures interactions; sensitive to scaling, can be unstable."],
    ["<font face='DJM'>'rbf'</font>", "Local, blob-shaped regions", "The default; controlled by <font face='DJM'>gamma</font>."],
    ["<font face='DJM'>'sigmoid'</font>", "S-shaped, like a tanh neuron", "Rarely the best; can behave erratically."],
], [COLW * 0.20, COLW * 0.34, COLW * 0.46], headbg=ACC, fs=7.15))
A(Spacer(1, 1.4))
A(F("RBF:  K(x, x') = exp( -gamma * ||x - x'||^2 )\n"
    "gamma='scale' (default) = 1 / (n_features * X.var())\n"
    "gamma='auto'            = 1 / n_features"))
A(P("<b>gamma</b> sets the reach of a single training point. Large &gamma; = tiny reach: each point influences only its "
    "immediate neighbourhood &rarr; wiggly boundary, overfitting. Small &gamma; = far reach &rarr; nearly linear, smooth, "
    "underfitting."))
A(P("<b>Scaling is mandatory:</b> the kernel is built from distances/inner products, so a feature measured in thousands "
    "swamps one measured in fractions. <b>Limits:</b> slow on large n (training is roughly quadratic), sensitive to C and "
    "&gamma;, no probability output unless <font face='DJM'>probability=True</font> (which is an extra internal "
    "cross-validation), and multiclass is handled by <b>OvO</b> (one-vs-one) rather than a single model."))
A(P("<b>Methods:</b> <font face='DJM'>fit</font> solves the quadratic program; <font face='DJM'>predict</font> returns "
    "labels; <font face='DJM'>decision_function</font> returns the signed distance to the boundary (magnitude &asymp; "
    "confidence, no 0&ndash;1 bound); <font face='DJM'>predict_proba</font> only when enabled; "
    "<font face='DJM'>support_vectors_</font> exposes the margin points."))
A(P("<b>In our program:</b> identical pipelines with linear / poly / RBF / sigmoid kernels on a 2-D toy set and on real "
    "features, a meshgrid + <font face='DJM'>contourf</font> plot of the decision boundary, and an explicit "
    "small-C vs large-C comparison with injected outliers to show margin width."))

# ============================== PAGE 3 =====================================
A(H("6 &middot; Ensembles: bagging, boosting, voting, stacking", ACC2))
A(T([
    ["Family", "How it works (what it reduces)", "Base learners", "Example"],
    ["<b>Bagging</b>", "Many models in <b>parallel</b> on bootstrap samples, then average/vote &mdash; cuts "
     "<i>variance</i>", "Deep, low-bias trees", "Random Forest"],
    ["<b>Pasting</b>", "Same, but sampling <b>without</b> replacement", "Trees", "&mdash;"],
    ["<b>Boosting</b>", "Sequential: each model fits the current errors/residuals, summed with a small learning "
     "rate &mdash; cuts <i>bias</i>", "Shallow stumps", "Gradient Boosting, AdaBoost, XGBoost"],
    ["<b>Voting</b>", "Different algorithms, combined by a <b>fixed</b> rule (labels or averaged probabilities)",
     "Any (mixed)", "sklearn voting"],
    ["<b>Stacking</b>", "Different algorithms, then a <b>meta-model</b> learns how to combine their predictions",
     "Any (mixed)", "sklearn stacking, our FDP net"],
], [COLW * 0.16, COLW * 0.47, COLW * 0.16, COLW * 0.21], headbg=ACC2, fs=7.0))
A(Spacer(1, 1.5))
A(P("<b>Why combine:</b> different models make different mistakes, so averaging <i>diverse</i> models cancels part of "
    "the error &mdash; averaging ten identical models does nothing. <b>Random Forest</b> = bagging + feature randomness "
    "(each split sees only <font face='DJM'>max_features</font> candidates), which decorrelates the trees. "
    "<b>Gradient Boosting</b> fits each shallow tree to the negative gradient (residual), scaled by "
    "<font face='DJM'>learning_rate</font>: stronger on tabular data, but easier to overfit and sensitive to noise."))
A(P("<b>Voting, hard vs soft:</b> <b>hard</b> counts predicted labels (majority). <b>Soft</b> averages predicted "
    "<i>probabilities</i> and takes the argmax &mdash; it keeps confidence information, so a single very sure model can "
    "outvote two unsure ones, and <font face='DJM'>weights=</font> only works with soft voting. Soft needs every model "
    "to expose probabilities."))
A(P("<b>Stacking:</b> the base models' predictions become the features for a second-level model (the <b>meta-learner</b>). "
    "Because it <i>learns</i> how much to trust each base model, it can beat a fixed vote &mdash; but the meta-features "
    "must come from <b>out-of-fold</b> predictions, otherwise the meta-learner sees scores from models that already "
    "memorised those rows (leakage), and it needs enough data to support a second level. "
    "<b>Confused with voting:</b> voting's combination rule is fixed and hand-chosen; stacking's is fitted."))
A(P("<b>Bayes Optimal Classifier:</b> the theoretically optimal combiner &mdash; average every hypothesis's prediction "
    "weighted by its posterior probability:"))
A(F("y = argmax_c  sum_h  P(c | x, h) * P(h | D)"))
A(P("It is optimal only if the hypothesis space and posteriors are exact, and is intractable in general; the lab "
    "approximates it with a <b>posterior-weighted soft vote</b> over a few models. When all the models are mediocre the "
    "weights are near-uniform, so the ensemble can land <i>below</i> its best member &mdash; combining is not "
    "automatically better. <b>In our program:</b> a manual majority vote "
    "(<font face='DJM'>np.column_stack</font> + <font face='DJM'>votes.sum(axis=1)</font>), "
    "<font face='DJM'>VotingClassifier(voting='soft')</font> with and without weights, a stacking net over concatenated "
    "base outputs, and a BOC from posterior weights."))

# ---------------------------------------------------------------- 7 --------
A(H("7 &middot; Hyperparameter optimisation", TEAL))
A(P("<b>Parameter vs hyperparameter:</b> a <b>parameter</b> is learned from data (split thresholds, SVM weights, network "
    "weights). A <b>hyperparameter</b> is chosen before training and controls <i>how</i> learning happens "
    "(<font face='DJM'>max_depth</font>, <font face='DJM'>C</font>, <font face='DJM'>alpha</font>, "
    "<font face='DJM'>n_estimators</font>, learning rate, k). Defaults are guesses; the best value depends on the "
    "dataset, so we search a <b>search space</b> of candidates scored by <b>cross-validation on training data</b>, never "
    "on test."))
A(T([
    ["Strategy", "How it explores", "Trade-off"],
    ["Manual", "You pick values by intuition, one run each", "Cheap to reason about, expensive in wall-clock, misses "
     "interactions"],
    ["Grid", "Every point of the Cartesian product", "Exhaustive and reproducible, but cost explodes with dimensions"],
    ["Random", "Sample <font face='DJM'>n_iter</font> points independently", "Better coverage per unit time in high "
     "dimensions; not exhaustive, so not guaranteed to find the grid's best"],
    ["Bayesian", "Fit a <b>surrogate</b> to past results, then sample where improvement is likely", "Fewer evaluations "
     "needed; needs a probabilistic model and a budget"],
], [COLW * 0.16, COLW * 0.44, COLW * 0.40], headbg=TEAL, fs=7.15))
A(Spacer(1, 1.5))
A(F("cost of a grid = product(len(values)) * cv_folds\n"
    "=> 3 hyperparams x 5 values x cv=5  =  375 fits"))
A(P("<b>Bayesian optimisation</b> = <i>surrogate model</i> + <i>acquisition function</i>. The surrogate estimates "
    "score(config); the acquisition balances <b>exploitation</b> (near known-good points) against <b>exploration</b> "
    "(uncertain regions)."))
A(T([
    ["Tool", "Key idea, and what you write"],
    ["<b>Hyperopt</b>", "You declare the space up front (<font face='DJM'>hp.choice</font> categorical, "
     "<font face='DJM'>hp.uniform</font> continuous, <font face='DJM'>hp.quniform</font> quantised, "
     "<font face='DJM'>hp.loguniform</font>) and write an objective returning a <b>loss</b>; "
     "<font face='DJM'>fmin</font> minimises it."],
    ["<b>TPE</b>", "Tree-structured Parzen Estimator, Hyperopt's default sampler: it models "
     "<font face='DJM'>P(config | good loss)</font> and <font face='DJM'>P(config | bad loss)</font> separately and "
     "samples where the good/bad ratio is highest &mdash; a density-ratio trick, not Gaussian processes. Selected by "
     "<font face='DJM'>algo=tpe.suggest</font>."],
    ["<b>Optuna</b>", "Define-by-run: the space is written <i>inside</i> the objective with "
     "<font face='DJM'>trial.suggest_*</font>, so later choices can depend on earlier ones; pruners kill unpromising "
     "trials early. You call <font face='DJM'>create_study(direction=...)</font> then "
     "<font face='DJM'>optimize</font>."],
], [COLW * 0.15, COLW * 0.85], headbg=TEAL, fs=7.1))
A(Spacer(1, 1.5))
A(P("<b>Why Hyperopt minimises:</b> optimisers are conventionally written to <i>minimise</i> a scalar "
    "(<font face='DJM'>status='ok'</font> only when the objective is minimised), so a maximisation task is passed as "
    "<b>negative</b> accuracy/loss &mdash; the best model is the <i>lowest</i> value. Optuna instead has an explicit "
    "<font face='DJM'>direction</font> (<font face='DJM'>'minimize'</font> is the default; "
    "<font face='DJM'>'maximize'</font> is set in the lab)."))
A(P("<b>Traps:</b> tuning on test (optimistic, unusable); comparing scores from different splits; an invalid value making "
    "every fit fail (reported as failed fits / NaN, not as a bad model). <b>In our program:</b> a manual loop, "
    "<font face='DJM'>GridSearchCV</font> over a 75-point grid, <font face='DJM'>RandomizedSearchCV(n_iter=100, cv=3)</font>, "
    "Hyperopt with TPE and Optuna &mdash; all on the same random forest, test held out until the end."))

# ============================== PAGE 4 =====================================
A(H("8 &middot; Neural networks: the basics", PURP))
A(P("<b>What:</b> a stack of layers of neurons. Each neuron computes a weighted sum of its inputs plus a bias, then "
    "passes it through a non-linear <b>activation</b>. Stacking lets the network build progressively abstract features."))
A(F("z = W.x + b        a = f(z)\n"
    "forward pass : input -> hidden layers -> output -> loss\n"
    "backprop     : loss -> dL/dw for every weight (chain rule)\n"
    "update       : w <- w - lr * dL/dw"))
A(P("<b>Why non-linearity:</b> without an activation, stacked linear layers collapse into a single linear map &mdash; "
    "depth would buy nothing."))
A(T([
    ["Piece", "What it does / why it exists"],
    ["<b>ReLU</b> <font face='DJM'>max(0,z)</font>", "Hidden layers. Cheap, no vanishing gradient for positive inputs; "
     "can 'die' (stuck at 0) if the learning rate is too high. Variants: LeakyReLU, ELU."],
    ["<b>sigmoid</b>", "Squashes to (0,1). Binary output unit (one neuron + binary cross-entropy). Saturates &rarr; "
     "vanishing gradients if used in deep hidden layers."],
    ["<b>softmax</b>", "Turns a vector of scores into probabilities that sum to 1. Multiclass output unit."],
    ["<b>Loss</b>", "The number being minimised: MSE for regression, cross-entropy for classification. It defines what "
     "'wrong' means."],
    ["<b>Optimizer</b>", "The update rule. <b>Adam</b> keeps a per-weight running average of gradient and squared "
     "gradient, giving each weight an adaptive step size &mdash; the robust default (<font face='DJM'>lr=0.001</font>)."],
    ["<b>Epoch / batch</b>", "One epoch = one pass over the whole training set. A batch is the chunk used for one "
     "weight update; <font face='DJM'>batch_size=32</font> means N/32 updates per epoch."],
    ["<b>Learning rate</b>", "Step size. Too high: the loss oscillates or diverges. Too low: training crawls or sticks "
     "in a plateau."],
    ["<b>Dropout</b>", "Randomly zeroes a fraction of activations during training only, forcing redundant representations "
     "and acting as regularisation. It is off at prediction time (<font face='DJM'>model.predict</font>)."],
], [COLW * 0.24, COLW * 0.76], headbg=PURP, fs=7.15))
A(Spacer(1, 1.5))
A(F("binary      : Dense(1, sigmoid)     + binary_crossentropy      labels 0/1\n"
    "multiclass  : Dense(k, softmax)     + categorical_crossentropy labels one-hot\n"
    "                                      sparse_categorical_...   labels integers"))
A(P("The three cross-entropies are the same idea for different label encodings &mdash; <b>sparse</b> just skips the "
    "one-hot step. Choosing the wrong pairing gives a shape/NaN error, not a silently worse model."))
A(P("<b>In our program:</b> <font face='DJM'>Sequential([Dense(32,relu), Dense(32,relu), Dense(1,sigmoid)])</font>, "
    "Adam + binary cross-entropy, <font face='DJM'>batch_size=32</font>, 15 epochs, then the same net with "
    "<font face='DJM'>Dropout(0.2)</font> to compare. <font face='DJM'>model.evaluate</font> returns "
    "<b>[loss, accuracy]</b> &mdash; loss first; <font face='DJM'>model.fit</font> returns a History whose "
    "<font face='DJM'>.history</font> holds per-epoch curves."))

# ---------------------------------------------------------------- 9 --------
A(H("9 &middot; Convolutional networks", ACC))
A(P("<b>Why not a dense net on images:</b> a 28&times;28 image is 784 inputs; the same image shifted by one pixel is a "
    "completely different input vector. Dense layers ignore that structure and need far too many weights."))
A(P("<b>What convolution does:</b> slide a small learnable <b>kernel</b> (e.g. 3&times;3) over the image, computing a "
    "product-sum at each position. The resulting <b>feature map</b> records <i>where</i> that pattern occurs; the same "
    "kernel is reused everywhere, so a feature learned in one corner is found in another (<b>translation "
    "invariance</b>) and the weight count stays tiny."))
A(F("output size = floor( (W - K + 2*P) / S ) + 1\n"
    "   W input, K kernel, P padding, S stride\n"
    "pool output = floor( (W - K) / S ) + 1"))
A(T([
    ["Layer / knob", "Purpose"],
    ["<font face='DJM'>Conv2D(filters, (k,k), padding, strides)</font>", "<b>filters</b> = how many patterns to learn "
     "(one feature map each); <b>kernel</b> = pattern size; <b>padding='same'</b> keeps the size, "
     "<font face='DJM'>'valid'</font> shrinks it; <b>stride</b> &gt; 1 subsamples while sliding."],
    ["<b>MaxPooling2D</b>", "Keeps the largest value per window &mdash; halves spatial size, keeps the strongest "
     "activation, adds small-shift robustness, no parameters."],
    ["<b>AveragePooling2D</b>", "Takes the mean &mdash; smoother, keeps overall strength rather than the peak."],
    ["<font face='DJM'>Flatten</font>", "Reshapes (h,w,c) into one long vector so a Dense layer can consume it. "
     "Preserves <i>all</i> spatial information, so it produces many features."],
    ["<font face='DJM'>GlobalAveragePooling2D</font>", "Averages each feature map to a single number &mdash; "
     "(h,w,c) &rarr; (c). Far fewer parameters, less overfitting, but loses location."],
], [COLW * 0.40, COLW * 0.60], headbg=ACC, fs=7.1))
A(Spacer(1, 1.5))
A(P("<b>In our program:</b> <font face='DJM'>Conv2D &rarr; MaxPool</font> &times;3, <font face='DJM'>Flatten</font> "
    "into <font face='DJM'>Dense(128)</font>, dropout, softmax head over 10 classes. Images are reshaped to "
    "<font face='DJM'>(-1, 28, 28, 1)</font> because Keras <b>always</b> expects a channel axis, and pixels are divided "
    "by 255 to keep gradients well-scaled. Augmentation (<font face='DJM'>ImageDataGenerator</font>) manufactures "
    "varied copies so the net cannot memorise exact pixel positions."))

# ---------------------------------------------------------------- 10 -------
A(H("10 &middot; Transfer learning", ACC2))
A(P("<b>Idea:</b> a network trained on a huge dataset (ImageNet: 1.2M images, 1000 classes) has already learned "
    "generic visual features in its early and middle layers &mdash; edges, textures, shapes. Those features transfer to "
    "new tasks. Training from scratch on a few thousand images learns noise; reusing a pretrained backbone does not."))
A(T([
    ["Pattern", "What you do", "When"],
    ["<b>Feature<br/>extract.</b>", "<font face='DJM'>include_top=False</font> (drop the 1000-class head), freeze the "
     "backbone (<font face='DJM'>layer.trainable=False</font>), attach your own head, train the head only.",
     "Small dataset, similar domain. Fast, safe."],
    ["<b>Fine-<br/>tuning</b>", "Unfreeze the top blocks (or everything) and continue training with a <i>much</i> smaller "
     "learning rate.", "More data / different domain. Can beat freezing, but easy to wreck the pretrained weights."],
], [COLW * 0.18, COLW * 0.52, COLW * 0.30], headbg=ACC2, fs=7.15))
A(Spacer(1, 1.5))
A(F("input (128,128,3) -> backbone -> (4,4,1280) -> GAP -> (1280,)\n"
    "              -> Dense(k, softmax)\n"
    "Grey images: Concatenate()([x,x,x]) to fake 3 channels"))
A(P("<b>Resize and rescale:</b> the backbone expects the size and normalisation it was trained with. VGG uses "
    "<font face='DJM'>preprocess_input</font> (BGR mean subtraction); <b>EfficientNetB0</b> expects raw 0&ndash;255 "
    "pixels, so a <font face='DJM'>Rescaling(255.0)</font> layer inside the model is correct &mdash; dividing by 255 as "
    "well silently degrades accuracy."))
A(P("<b>Why pretrained wins:</b> it starts from features shaped by far more data, so it needs fewer epochs and "
    "generalises better. <b>VGG16/VGG19</b> have 16/19 layers of 3&times;3 convs and ~138M parameters &mdash; simple but "
    "heavy; <b>EfficientNet</b> scales depth, width and resolution together for similar accuracy at far lower cost. "
    "Extra <font face='DJM'>Conv2D</font>+<font face='DJM'>BatchNorm</font> blocks on top adapt frozen features to a new "
    "domain."))
A(P("<b>In our program:</b> VGG16 and EfficientNetB0 on Fashion-MNIST, VGG16/VGG19 with and without extra conv blocks on a "
    "4-class medical image set, and a stacking model where <b>three frozen CNNs</b> produce probability vectors that are "
    "concatenated and fed to a small dense head (<font face='DJM'>keras.Model(inputs, outputs)</font> packages that graph; "
    "it builds no layers itself)."))

# ---------------------------------------------------------------- 11 -------
A(H("11 &middot; The functions you must be able to explain", TEAL))
A(T([
    ["Function", "What it does, and the traps"],
    ["<font face='DJM'>train_test_split</font>", "Shuffles and splits into "
     "<b>X_train, X_test, y_train, y_test</b> (that order). <font face='DJM'>test_size</font> is the fraction held out; "
     "<font face='DJM'>random_state</font> fixes the shuffle (reproducibility, not accuracy); "
     "<font face='DJM'>stratify=y</font> keeps class proportions in both halves. Splitting first is what prevents leakage."],
    ["<font face='DJM'>StandardScaler</font>", "(x &minus; &mu;) / &sigma; per feature &rarr; mean 0, sd 1. "
     "<font face='DJM'>fit</font> <b>learns</b> &mu; and &sigma; only; <font face='DJM'>transform</font> applies them; "
     "<font face='DJM'>fit_transform</font> does both. Fit on <b>train only</b> &mdash; using test data would leak its "
     "mean/spread into training and inflate the score. Needed by distance/gradient methods (KNN, SVM, NN, k-means), "
     "irrelevant to trees."],
    ["<font face='DJM'>Pipeline</font>", "Chains steps so they are fitted and applied in order, and makes CV leak-free "
     "automatically. Parameters are addressed as <font face='DJM'>step__param</font> (double underscore)."],
    ["<font face='DJM'>SelectKBest(.., k)</font>", "Univariate <b>filter</b>: scores each feature independently "
     "(<font face='DJM'>f_classif</font> = ANOVA F) and keeps the top k. Blind to interactions, so it can discard a feature "
     "that only matters in combination. 'all' keeps everything."],
    ["<font face='DJM'>GridSearchCV</font>, <font face='DJM'>Randomized<br/>SearchCV</font>", "Exhaustive grid vs <font face='DJM'>n_iter</font> "
     "samples; both CV-score every candidate, expose <font face='DJM'>best_params_</font> and "
     "<font face='DJM'>best_estimator_</font>, and <font face='DJM'>refit</font> the winner on all training data."],
], [COLW * 0.30, COLW * 0.70], headbg=TEAL, fs=6.95, maxrows=4))

A(P("<b>Also know:</b> <b>MultinomialNB</b> = counts, <b>GaussianNB</b> = continuous; <b>precision</b> = purity of "
    "positive calls, <b>recall</b> = coverage; <b>voting</b> uses a fixed rule (hard = label poll, soft = averaged "
    "probabilities), <b>stacking</b> a learned meta-model. <b>MinMaxScaler</b> maps to [0,1] (one outlier squashes "
    "everything; images just use /255). <b>accuracy_score</b> hides imbalance &mdash; read "
    "<font face='DJM'>classification_report</font> and <font face='DJM'>confusion_matrix</font> (rows actual, cols "
    "predicted).", SMALL))

# ---------------------------------------------------------------- 12 -------
A(H("12 &middot; Pairs people mix up, and the one-line answer", NAVY))
A(T([
    ["Pair", "The distinction to say out loud"],
    ["Parameter vs hyperparameter", "Learned from data vs chosen before training."],
    ["Gini vs entropy", "1&minus;&Sigma;p&sup2; vs &minus;&Sigma;p&thinsp;log p; both 0 when pure; similar trees, gini cheaper."],
    ["KNN vs K-Means", "Supervised, uses labels, k = neighbours vs unsupervised clustering, k = centroids."],
    ["Bagging vs boosting", "Parallel on resamples (variance) vs sequential on residuals (bias)."],
], [COLW * 0.32, COLW * 0.68], headbg=NAVY, fs=7.3, maxrows=5))

A(H("13 &middot; Self-check", TEAL))
A(P("<b>Tree?</b> greedy impurity-drop splits, root&rarr;leaf routing, pruning fights overfitting. "
    "<b>Kernels?</b> only <font face='DJM'>K(x,x')=&phi;(x)&middot;&phi;(x')</font> is needed, so a linear boundary in "
    "&phi;-space is curved in the input space. <b>Multinomial vs Gaussian NB?</b> counts vs continuous-normal features. "
    "<b>Why tune?</b> defaults are guesses; CV on training folds estimates generalisation on unseen folds. "
    "<b>CNN layers?</b> conv = patterns, pool = shrink, Flatten/GAP = vector, softmax = scores. "
    "<b>Ensembles?</b> parallel resamples / sequential residuals / fixed rule / learned meta-model. "
    "<b>Laplace?</b> a zero count vetoes the class; &alpha; keeps likelihoods non-zero. "
    "<b>Scaler on train only?</b> its &mu;,&sigma; must not come from test.", SMALL))

# ------------------------------------------------------------------ build --
OUT = "/home/user/idek/ML_Lab_Concept_Notes.pdf"


class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        BaseDocTemplate.__init__(self, fn, pagesize=A4, leftMargin=LM,
                                 rightMargin=RM, topMargin=TM, bottomMargin=BM,
                                 title="Machine Learning - Concept Notes (4 pages)",
                                 author="Built from the ML lab notebooks",
                                 subject="Concept-first revision: what each algorithm is, why, how, and what the code does",
                                 **kw)
        f1 = Frame(LM, BM, COLW, PH - TM - BM, id="c1",
                   leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        f2 = Frame(LM + COLW + GUT, BM, COLW, PH - TM - BM, id="c2",
                   leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="two", frames=[f1, f2],
                                           onPage=self.deco)])

    def deco(self, canv, doc):
        canv.saveState()
        canv.setFont("DJ", 6.6)
        canv.setFillColor(GREY)
        canv.drawString(LM, PH - TM + 3.2 * mm, "Machine Learning \u00b7 concept notes")
        canv.drawRightString(PW - RM, PH - TM + 3.2 * mm, "Page %d of 4" % doc.page)
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(LM, BM - 3.0 * mm, PW - RM, BM - 3.0 * mm)
        canv.setStrokeColor(colors.HexColor("#e3e8ee"))
        canv.line(LM + COLW + GUT / 2, BM, LM + COLW + GUT / 2, PH - TM)
        canv.restoreState()


A(PEND and Pend(PEND) or [])
Doc(OUT).build(STORY)
print("built", OUT)
from pypdf import PdfReader
print("PAGES:", len(PdfReader(OUT).pages))
