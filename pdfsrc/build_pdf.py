#!/usr/bin/env python3
"""Build the 4-page ML lab quiz revision PDF from the audited notebooks."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether, Flowable,
                                CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJM", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DJMB", FD + "DejaVuSansMono-Bold.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DJ", normal="DJ", bold="DJB", italic="DJ", boldItalic="DJB")

INK = colors.HexColor("#14213d")
NAVY = colors.HexColor("#1d3557")
ACCENT = colors.HexColor("#b23a48")
ACC2 = colors.HexColor("#2a6f97")
TEAL = colors.HexColor("#0b6e4f")
GREY = colors.HexColor("#4a4e57")
BG = colors.HexColor("#eef2f7")
BG2 = colors.HexColor("#f7f3ea")
RULE = colors.HexColor("#c9d3df")

BODY = ParagraphStyle("body", fontName="DJ", fontSize=8.55, leading=10.9,
                      textColor=INK, alignment=TA_LEFT, spaceAfter=0)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.9, leading=10.0)
CODE = ParagraphStyle("code", fontName="DJM", fontSize=7.15, leading=8.9,
                      textColor=colors.HexColor("#16324f"), leftIndent=2.5,
                      spaceBefore=1.2, spaceAfter=1.2, backColor=BG,
                      borderPadding=(1.6, 3, 1.6, 3))
H1 = ParagraphStyle("h1", fontName="DJB", fontSize=13.2, leading=14.6,
                    textColor=colors.white, spaceAfter=0)
H2 = ParagraphStyle("h2", fontName="DJB", fontSize=10.0, leading=11.8,
                    textColor=colors.white, spaceBefore=3.0, spaceAfter=2.2)
H3 = ParagraphStyle("h3", fontName="DJB", fontSize=8.7, leading=10.6,
                    textColor=NAVY, spaceBefore=2.6, spaceAfter=0.8)
TICK = ParagraphStyle("tick", parent=BODY, leftIndent=6.5, bulletIndent=1.2,
                      spaceAfter=0.9)
TICKS = ParagraphStyle("ticks", parent=SMALL, leftIndent=6.5, bulletIndent=1.2,
                       spaceAfter=0.7)

def P(t, s=BODY): return Paragraph(t, s)
def B(t): return Paragraph(t, TICK, bulletText="•")
def S(t): return Paragraph(t, TICKS, bulletText="–")
def CB(t):
    para = Paragraph(t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                     .replace("\n", "<br/>"), CODE)
    # keep short code blocks on one column so a snippet never splits in two
    if t.count("\n") <= 8:
        return KeepTogether([para])
    return para

def H(t, color=NAVY):
    tbl = Table([[Paragraph(t, H2)]], colWidths=["100%"])
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color),
                             ("LEFTPADDING", (0, 0), (-1, -1), 4),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                             ("TOPPADDING", (0, 0), (-1, -1), 2),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4)]))
    # keep a heading with the paragraph that follows it
    return [CondPageBreak(42 * mm), Spacer(1, 2.5), tbl, Spacer(1, 3.2)]

def h3(t, c=NAVY): return Paragraph(t, ParagraphStyle("h3c", parent=H3, textColor=c))

def mini_table(rows, widths, headbg=NAVY, fs=7.35, zebra=True, keep=False):
    data = [[Paragraph(c, ParagraphStyle("th", fontName="DJB", fontSize=fs,
                                         leading=fs + 1.7, textColor=colors.white))
             for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(c, ParagraphStyle("td", fontName="DJ", fontSize=fs,
                                                 leading=fs + 1.7, textColor=INK))
                     for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), headbg),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 3),
          ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
          ("TOPPADDING", (0, 0), (-1, -1), 1.5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
          ("LINEBELOW", (0, 0), (-1, 0), 0.7, headbg),
          ("GRID", (0, 0), (-1, -1), 0.3, RULE)]
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f2f5f9")))
    t.setStyle(TableStyle(st))
    if len(data) <= 10:
        return KeepTogether([t])
    return t

class Rule(Flowable):
    def __init__(self, w, col=RULE, th=0.7):
        Flowable.__init__(self); self.w = w; self.col = col; self.th = th
    def wrap(self, aw, ah): return (self.w, self.th + 2)
    def draw(self):
        self.canv.setStrokeColor(self.col); self.canv.setLineWidth(self.th)
        self.canv.line(0, 1, self.w, 1)

PW, PH = A4
LM = RM = 12.5 * mm
TM = 11.5 * mm
BM = 10.0 * mm
GUT = 6.4 * mm
COLW = (PW - LM - RM - GUT) / 2.0

# ----------------------------------------------------------------- content ---
STORY = []

def A(x):
    if isinstance(x, (list, tuple)):
        STORY.extend(x)
    else:
        STORY.append(x)

# ============================== PAGE 1 =====================================
banner = Table([[Paragraph("ML Lab Quiz Revision &mdash; all 11 notebooks",
                           ParagraphStyle("bt", fontName="DJB", fontSize=11.6,
                                          leading=13.4, textColor=colors.white))],
                [Paragraph("20 questions &times; 1 mark &middot; 30 minutes &nbsp;|&nbsp; "
                           "repository 120hertzyt-maker/idek &middot; branch <b>main</b> &middot; "
                           "all numbers are saved notebook outputs",
                           ParagraphStyle("bs", fontName="DJ", fontSize=6.6,
                                          leading=8.4, textColor=colors.HexColor("#cbd8e8")))]],
               colWidths=[COLW])
banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, 0), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
                            ("TOPPADDING", (0, 1), (-1, 1), 0),
                            ("BOTTOMPADDING", (0, 1), (-1, 1), 4.5)]))
A(banner); A(Spacer(1, 4))

A(P("<b>11 notebooks = 11 labs &middot; 198 code cells &middot; 167 markdown cells &middot; "
    "14 TODO/reflection cells &middot; 0 error outputs.</b> Every figure below is a <i>saved</i> notebook "
    "output, not a re-run. <font face='DJM'>CNN_Hands_on_Sansera</font> and "
    "<font face='DJM'>06_07_2026_FDP_Day_1_CNN</font> are identical in content &mdash; one lab, two copies.", SMALL))
A(Spacer(1, 3))

# ---------------- LAB 1 ----------------
A(H("1 &middot; Decision Tree &mdash; Breast Cancer (Exploratory Lab 2.0)", ACC2))
A(P("<b>Objective:</b> see how a tree actually behaves &mdash; split criterion, depth, pruning &mdash; "
    "not just <font face='DJM'>.fit()</font>. Data: <font face='DJM'>load_breast_cancer()</font>, 569&times;30, "
    "binary target: <b>0 = malignant (212, 37.3%)</b>, <b>1 = benign (357, 62.7%)</b>."))
A(Spacer(1, 1.5))
A(CB("X = pd.DataFrame(data.data, columns=data.feature_names)\n"
     "y = pd.Series(data.target)   # 0=malignant, 1=benign\n"
     "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2,\n"
     "                         random_state=42, stratify=y)  # 455 / 114"))
A(Spacer(1, 1.5))
A(h3("Key results (saved outputs)"))
A(mini_table([
    ["Experiment", "Test acc", "Notes"],
    ["Baseline tree (defaults)", "0.9123", "depth 7, 19 leaves"],
    ["Gini vs Entropy", "0.9123 / 0.9123", "depth 7 vs 6"],
    ["Sweep max_depth 1&ndash;20", "<b>0.9386 @ d=3</b>", "train at d=3 = 0.9758"],
    ["Pruning ccp_alpha", "~0.939 @ .003&ndash;.008", "&gt;.014 &rarr; 0.895"],
    ["GridSearchCV", "0.9386", "gini, max_depth=4"],
], [COLW * 0.40, COLW * 0.235, COLW * 0.365]))
A(Spacer(1, 1.5))
A(B("<b>Impurity:</b> Gini = 1 &minus; &Sigma;p<sub>i</sub><sup>2</sup> (default); "
    "Entropy = &minus;&Sigma;p<sub>i</sub>log<sub>2</sub>p<sub>i</sub>. Same accuracy here, "
    "<i>different trees</i> &mdash; clean separable data makes both rank splits alike."))
A(B("<b>Overfitting curve:</b> train acc &rarr; 1.00 by depth 7 while test stalls at 0.913. "
    "Best test accuracy sits at low complexity (d=3), the classic U-curve."))
A(B("<b>Two ways to simplify:</b> <font face='DJM'>max_depth</font> stops growth (pre-pruning); "
    "<font face='DJM'>ccp_alpha</font> grows the full tree then trims it (post-pruning) via "
    "<font face='DJM'>cost_complexity_pruning_path()</font>; <font face='DJM'>ccp_alphas = path.ccp_alphas[:-1]</font> "
    "drops the trivial single-node alpha."))
A(B("<b>Grid search:</b> 2 criteria &times; 7 depths ([3,4,5,6,7,8,None]) = 14 &times; cv=5 = <b>70 fits</b>. "
    "<font face='DJM'>max_depth=None</font> = grow until natural stopping. "
    "Attributes: <font face='DJM'>best_params_, best_score_ (0.9385 CV), best_estimator_</font>."))
A(B("<b>Feature importance</b> (<font face='DJM'>feature_importances_</font>, sums to 1): "
    "worst radius <b>0.7335</b>, worst concave points 0.1220, texture error 0.0458 &mdash; "
    "and the root split <i>is</i> worst radius, because the root sees 100% of samples."))
A(B("<b>Error profile matters:</b> shallow d=2 (0.895) has fewest missed cancers (2) but most false alarms (10); "
    "d=20 (0.912) keeps missed cancers at 3 but doubles false alarms to 7. Accuracy alone hides this."))
A(B("<font face='DJM'>plot_tree(model, feature_names=, class_names=, filled=True, rounded=True, max_depth=3)</font>; "
    "<font face='DJM'>get_depth()</font>, <font face='DJM'>get_n_leaves()</font> are query methods, not parameters."))

# ---------------- LAB 2 ----------------
A(H("2 &middot; Week 4 &mdash; Manual vs Grid vs Randomized Search (KNN &amp; DT)", ACC2))
A(P("<b>Objective:</b> tune DT and KNN by hand, with <font face='DJM'>GridSearchCV</font> and with "
    "<font face='DJM'>RandomizedSearchCV</font>, then combine them in a voting classifier. "
    "4 datasets: Wine Quality, HR Attrition, Banknote, QSAR Biodegradation."))
A(Spacer(1, 1.5))
A(CB("Pipeline([('scaler', StandardScaler()),\n"
     "          ('feature_selection', SelectKBest(f_classif)),\n"
     "          ('classifier', KNeighborsClassifier())])\n"
     "# grid keys MUST use step prefixes:\n"
     "{'scaler': [StandardScaler(), MinMaxScaler()],\n"
     " 'feature_selection__k': [8, 10, 'all'],\n"
     " 'classifier__n_neighbors': [3, 5, 7],\n"
     " 'classifier__weights': ['distance'],\n"
     " 'classifier__metric': ['euclidean', 'manhattan']}"))
A(Spacer(1, 1.5))
A(B("<b>Manual search:</b> <font face='DJM'>itertools.product(*values)</font> &rarr; "
    "<font face='DJM'>dict(zip(keys, v))</font>; scored by mean 5-fold "
    "<font face='DJM'>roc_auc_score</font> on <font face='DJM'>predict_proba(X)[:, 1]</font>; "
    "<font face='DJM'>best_score = -1</font> sentinel."))
A(B("<b>Built-in:</b> <font face='DJM'>GridSearchCV(..., scoring='roc_auc', cv=StratifiedKFold(5, shuffle=True), n_jobs=-1)</font>; "
    "<font face='DJM'>RandomizedSearchCV(..., n_iter=10, param_distributions=...)</font> with "
    "<font face='DJM'>scipy.stats.randint</font> ranges. Same winners as the manual search (e.g. Wine DT entropy/d=6/msl=5)."))
A(B("<b>Voting:</b> <font face='DJM'>VotingClassifier(estimators=[...], voting='soft')</font> averages probabilities; "
    "the manual version takes <font face='DJM'>np.mean(votes) &gt; 0.5</font>. Hard voting = majority label."))
A(B("<b>Scaling insight:</b> KNN is distance-based so it needs scaling &amp; prefers StandardScaler here; "
    "the tree ignores scale but the grid still picks MinMaxScaler sometimes. <font face='DJM'>SelectKBest(f_classif)</font> "
    "is a filter (ANOVA F) &mdash; it is <i>inside</i> the pipeline so it is refit per fold (no leakage)."))
A(mini_table([
    ["Dataset (winner)", "DT acc / AUC", "KNN acc / AUC"],
    ["Wine Quality", "0.7229 / 0.7897", "<b>0.7583 / 0.8707</b>"],
    ["Banknote (4 feats)", "0.9927 / 0.9928", "<b>1.0000 / 1.0000</b>"],
    ["QSAR", "0.7666 / 0.8134", "<b>0.8517 / 0.8905</b>"],
    ["HR Attrition", "file not found &rarr; skipped", "&mdash;"],
], [COLW * 0.34, COLW * 0.33, COLW * 0.33]))
A(Spacer(1, 1.5))
A(B("Wine target engineered as <font face='DJM'>good_quality = (quality &gt; 5)</font>; read with <font face='DJM'>sep=';'</font>. "
    "Voting on Wine: manual 0.7333 vs built-in 0.7729 &mdash; ensembles can lose to their best member."))

# ---------------- LAB 3 ----------------
A(H("3 &middot; Lab 7 &mdash; Naive Bayes from scratch to Bayes Optimal", ACC2))
A(P("<b>Objective:</b> implement Multinomial NB in NumPy, prove it equals sklearn, then tune smoothing "
    "&alpha; and feature representation. Data: PubMed 20k RCT sentences, <b>180,040</b> train lines, "
    "5 roles (BACKGROUND / OBJECTIVE / METHODS / RESULTS / CONCLUSIONS); METHODS &asymp; 33%, OBJECTIVE &asymp; 7.7%."))
A(Spacer(1, 1.5))
A(CB("c_hat = argmax_c P(c) * prod_i P(w_i|c)^x_i        # product form\n"
     "log P(c) + sum_i x_i * log P(w_i|c)                # what code does\n"
     "P(w_i|c) = (count(w_i,c) + alpha) / (sum_j count(w_j,c) + alpha*V)\n"
     "prior P(c) = rows in c / n_samples                  # ROWS, not words"))
A(Spacer(1, 1.5))
A(CB("class NaiveBayesClassifier:            # alpha = Laplace smoothing\n"
     "  fit: class_log_prior_ (n_classes,) ; feature_log_prob_ (n_class, V)\n"
     "  predict_log_scores: X @ self.feature_log_prob_.T + self.class_log_prior_\n"
     "  predict: self.classes_[np.argmax(scores, axis=1)]   # map idx -> label"))
A(Spacer(1, 1.5))
A(B("<b>Why log space:</b> 25 probabilities &asymp;10<sup>&minus;5</sup> each underflow to 0.0; logs turn the product into a sum."))
A(B("<b>Why &alpha;:</b> one unseen word would zero the whole product; smoothing adds a pseudo-count and "
    "<b>&alpha;V</b> in the denominator keeps it a distribution."))
A(B("<b>Verification cell (the real test):</b> |&Delta;prior| and |&Delta;likelihood| &lt; 1e&minus;10 vs "
    "<font face='DJM'>MultinomialNB(alpha=1.0)</font>, plus &gt;99.9% prediction agreement. A wrong NB still "
    "classifies &mdash; accuracy is a weak test."))
A(mini_table([
    ["Model", "Acc", "Macro-F1"],
    ["Custom NB, counts, &alpha;=1", "0.7226", "0.6567"],
    ["TF-IDF untuned (worse!)", "0.6950", "0.5783"],
    ["TF-IDF bigrams, &alpha;=0.1", "<b>0.7416</b>", "<b>0.6632</b>"],
], [COLW * 0.56, COLW * 0.22, COLW * 0.22]))
A(Spacer(1, 1.5))
A(B("<b>Why untuned TF-IDF loses:</b> TF-IDF values are L2-normalised fractions &lt; 1, so "
    "<font face='DJM'>alpha=1.0</font> swamps the real signal. Tune &alpha; with the representation "
    "(best &alpha; on <b>dev</b> = 1.0 for counts)."))
A(B("<b>Dev vs test protocol:</b> &alpha; and n-gram range chosen on dev; test scored once. Tuning on test makes "
    "the score a maximum over settings = optimistically biased, and a bigger test set does not fix that."))
A(B("<b>CountVectorizer(min_df=2, stop_words='english')</b> is fit on <b>train only</b>; "
    "<font face='DJM'>ngram_range=(1,2)</font> buys phrases (&quot;double blind&quot;) at the cost of a bigger V "
    "and a bigger &alpha;V."))
A(B("<b>Bayes Optimal Classifier:</b> P(c|x,D) = &Sigma;<sub>h</sub> P(c|x,h)&middot;P(h|D); here "
    "<i>approximated</i> by <font face='DJM'>VotingClassifier(voting='soft', weights=posterior_weights)</font>. "
    "Weights = softmax of mean held-out log-likelihood; the <i>exact</i> sum-version collapses onto one model."))
A(B("<b>Result:</b> BOC &asymp;0.590 lost to LogisticRegression alone &asymp;0.625 &mdash; averaging helps only when "
    "members make <i>different</i> mistakes. &quot;Optimal&quot; is a claim about the true hypothesis space, not a promise."))

# ---------------- LAB 4 ----------------
A(H("4 &middot; Week 10 &mdash; SVM kernels and margins", ACC2))
A(P("<b>Objective:</b> train SVMs with <b>linear, RBF and poly</b> kernels on 3 datasets, then compare hard vs soft margins."))
A(Spacer(1, 1.5))
A(CB("SVC(kernel='linear'|'rbf'|'poly', gamma='auto', random_state=42)\n"
     "gamma='auto'  ->  1 / n_features        # 'scale' = 1/(n_features*X.var())\n"
     "StandardScaler().fit_transform(X_train) ; .transform(X_test)   # fit train only"))
A(Spacer(1, 1.5))
A(mini_table([
    ["Dataset", "linear", "rbf", "poly"],
    ["Moons (500, noise=.2)", "0.87", "<b>0.97</b>", "0.89"],
    ["Banknote (variance+skewness)", "0.88", "<b>0.93</b>", "0.84"],
], [COLW * 0.46, COLW * 0.18, COLW * 0.18, COLW * 0.18]))
A(Spacer(1, 1.5))
A(B("<b>Kernel trick:</b> map to a higher-dimensional space where a linear hyperplane becomes a curved "
    "boundary here. Linear = straight; RBF = local/circular; poly = polynomial curve."))
A(B("<b>Moons</b> is non-linear &rarr; linear tops out at 0.87, RBF nearly perfect. <b>Banknote</b> uses only "
    "2 of 4 features, so no kernel is perfect."))
A(B("<b>Margins:</b> <font face='DJM'>C</font> = inverse regularisation. C=0.1 (soft) &rarr; wide margin, "
    "tolerates points inside it; C=100 (hard) &rarr; narrow margin, fits outliers &rarr; overfits. "
    "Data: <font face='DJM'>make_blobs(100, centers=2, cluster_std=0.6)</font> + 2 outliers."))
A(B("<b>Boundary recipe:</b> <font face='DJM'>h=.02</font> meshgrid &rarr; <font face='DJM'>np.c_[xx.ravel(), yy.ravel()]</font> "
    "&rarr; predict &rarr; <font face='DJM'>Z.reshape(xx.shape)</font> &rarr; <font face='DJM'>contourf</font>."))

# ---------------- LAB 5 ----------------
A(H("5 &middot; ML Models &amp; Ensemble (ovariantotal.csv)", ACC2))
A(P("<b>Objective:</b> benchmark 5 single classifiers vs RF, gradient boosting and a hand-built "
    "max-vote ensemble. 349&times;50, target <font face='DJM'>TYPE</font>, "
    "<font face='DJM'>test_size=0.25</font> &rarr; 88 test rows."))
A(Spacer(1, 1.5))
A(mini_table([
    ["Model (exact params)", "Acc"],
    ["LogisticRegression(max_iter=21)", "<b>0.8977</b>"],
    ["SVC(linear, C=0.004, ovr)", "0.8750"],
    ["GaussianNB()", "0.8523"],
    ["RandomForest(n_est=50, max_feat='sqrt', msl=35)", "0.8523"],
    ["GradientBoosting(learning_rate=0.1)", "0.8523"],
    ["KNeighbors(n_neighbors=3)", "0.8409"],
    ["DecisionTree(gini, ccp_alpha=.06, mss=5, msl=5)", "0.8182"],
    ["SVC rbf .9", "0.7955"], ["SVC sigmoid .9", "0.7841"], ["SVC poly", "0.6705"],
], [COLW * 0.77, COLW * 0.23]))
A(Spacer(1, 1.5))
A(B("<b>Voting ensemble:</b> stack the four prediction columns with "
    "<font face='DJM'>np.column_stack</font>, then take the majority by "
    "<font face='DJM'>votes.sum(axis=1) &gt; 2</font> &rarr; 0.8750; a 2&ndash;2 tie falls to class <b>0</b>."))
A(B("Poly kernel collapses to predicting class 1 (recall 0.95, precision 0.61) &rarr; the confusion matrix, not "
    "accuracy, exposes it."))
A(B("<b>Notebook quirk:</b> the second bar chart is labelled &quot;XGBoost&quot; but the model actually trained is "
    "<font face='DJM'>GradientBoostingClassifier</font>, and the values are hard-coded lists, not computed."))

# ---------------- LAB 6 ----------------
A(H("6 &middot; Hyperparameter optimisation (diabetes.csv)", ACC2))
A(P("<b>Objective:</b> compare manual tuning, <font face='DJM'>RandomizedSearchCV</font>, "
    "<font face='DJM'>GridSearchCV</font>, Bayesian optimisation (Hyperopt) and Optuna. "
    "Data 768&times;9, <font face='DJM'>Outcome</font> 500/268; zeros in Glucose replaced by the median via "
    "<font face='DJM'>np.where</font>."))
A(Spacer(1, 1.5))
A(mini_table([
    ["Technique", "Test acc"],
    ["RF(n_estimators=10) baseline", "0.7922"],
    ["Manual (300 trees, entropy, msl=10)", "0.8247"],
    ["RandomizedSearchCV (n_iter=100, cv=3)", "<b>0.8312</b>"],
    ["GridSearchCV refine (75&times;10 = 750 fits)", "0.8117"],
    ["Hyperopt TPE (max_evals=80)", "0.8117"],
], [COLW * 0.72, COLW * 0.28]))
A(Spacer(1, 1.5))
A(B("<b>Randomized</b> samples <font face='DJM'>n_iter</font> combinations from distributions "
    "(<font face='DJM'>param_distributions</font>); <b>Grid</b> tries every point of "
    "<font face='DJM'>param_grid</font> &mdash; here 1&times;1&times;1&times;3&times;5&times;5 = 75 &times; cv=10."))
A(B("<b>Hyperopt:</b> <font face='DJM'>hp.choice</font> (categorical), <font face='DJM'>hp.quniform</font> + "
    "<font face='DJM'>scope.int</font> (integer grid), <font face='DJM'>hp.uniform</font> (continuous). "
    "<font face='DJM'>fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=80, trials=Trials())</font>. "
    "TPE = Tree-structured Parzen Estimator, the surrogate model."))
A(B("<b>Loss is negative accuracy</b> (&minus;0.95 &lt; &minus;0.80) because <font face='DJM'>fmin</font> minimises; "
    "return <font face='DJM'>{'loss': ..., 'status': STATUS_OK}</font>."))
A(B("<b>Optuna:</b> <font face='DJM'>create_study(direction='maximize')</font> + "
    "<font face='DJM'>trial.suggest_int / suggest_float(log=True) / suggest_categorical</font>, "
    "<font face='DJM'>n_trials=100</font>, read <font face='DJM'>study.best_params</font>."))
A(B("<b>Trap:</b> <font face='DJM'>max_features='auto'</font> is removed in modern sklearn &rarr; "
    "<font face='DJM'>InvalidParameterError</font>, <b>105 of 300 fits failed</b> and scores became NaN "
    "(<font face='DJM'>FitFailedWarning</font>). Use <font face='DJM'>'sqrt'</font> or <font face='DJM'>'log2'</font>."))

# ---------------- LAB 7 ANN ----------------
A(H("7 &middot; ANN hands-on (Keras, ovariantotal.csv)", ACC2))
A(P("<b>Objective:</b> first feed-forward network; add dropout; read the confusion matrix. "
    "349&times;50, <font face='DJM'>MinMaxScaler</font>, <font face='DJM'>test_size=0.2, random_state=0</font>, 49 inputs."))
A(Spacer(1, 1.5))
A(CB("model = Sequential()\n"
     "model.add(Dense(32, activation='relu', input_dim=49))\n"
     "model.add(Dense(32, activation='relu'))\n"
     "model.add(Dense(1,  activation='sigmoid'))     # binary -> 1 unit\n"
     "model.compile(optimizer='adam', loss='binary_crossentropy',\n"
     "              metrics=['accuracy'])\n"
     "model.fit(X_train, y_train, batch_size=32, epochs=15)\n"
     "y_pred = np.where(model.predict(X_test) > 0.5, 1, 0).astype(int)"))
A(Spacer(1, 1.5))
A(B("Plain ANN: CM <font face='DJM'>[[32, 9], [3, 26]]</font> &rarr; acc <b>0.8286</b>. "
    "After <font face='DJM'>Dropout(0.2)</font> on both hidden layers: <font face='DJM'>[[33, 8], [3, 26]]</font> &rarr; "
    "<b>0.8429</b>, fewer false positives."))
A(B("<b>sigmoid + 1 unit + binary_crossentropy</b> for binary; <b>softmax + n units + "
    "categorical/sparse_categorical_crossentropy</b> for multiclass. Predictions are probabilities &mdash; "
    "you must threshold at 0.5 yourself."))
A(B("<b>Confusion matrix:</b> TP = predicted 1 &amp; actual 1; FP = Type I error; FN = Type II error; "
    "TN = both 0. Rows = actual, columns = predicted (<font face='DJM'>confusion_matrix(y_true, y_pred)</font>)."))
A(B("<b>Quirk:</b> the notebook also builds a <font face='DJM'>StandardScaler</font> but trains on the "
    "<font face='DJM'>MinMaxScaler</font> output (<font face='DJM'>X_scale</font>) &mdash; scaling choice is "
    "whichever array is passed to <font face='DJM'>train_test_split</font>."))

# ---------------- LAB 8 CNN ----------------
A(H("8 &middot; CNN on Fashion-MNIST + transfer learning", ACC2))
A(P("<b>Objective:</b> build a CNN from scratch, then reuse ImageNet backbones. Data 60,000&times;28&times;28 train / "
    "10,000 test, 10 classes. <i>Identical to FDP Day 1 notebook.</i>"))
A(Spacer(1, 1.5))
A(CB("x = x.astype('float32') / 255.0        # [0,255] -> [0,1]\n"
     "x = x.reshape(-1, 28, 28, 1)           # -1 = keep sample count\n"
     "ImageDataGenerator(rotation_range=10, width_shift_range=0.1,\n"
     "  height_shift_range=0.1, zoom_range=0.1, shear_range=0.1,\n"
     "  fill_mode='nearest')                 # test_gen has NO augmentation\n"
     "Conv2D(32,(3,3),relu) -> MaxPool(2,2) -> Conv2D(64) -> MaxPool\n"
     "  -> Conv2D(128) -> MaxPool -> Flatten -> Dense(128) -> Dropout(.5)\n"
     "  -> Dense(10, softmax)                # sparse_categorical_crossentropy"))
A(Spacer(1, 1.5))
A(mini_table([
    ["Model", "Test acc"],
    ["CNN from scratch (10 epochs)", "0.8625"],
    ["VGG16 frozen + new head", "0.8854"],
    ["EfficientNetB0 frozen + head", "<b>0.8926</b>"],
], [COLW * 0.68, COLW * 0.32]))
A(Spacer(1, 1.5))
A(B("<b>Grayscale &rarr; RGB:</b> <font face='DJM'>Concatenate()([x, x, x])</font>; VGG16 needs 128&times;128 so a "
    "<font face='DJM'>Resizing(128,128)</font> layer sits inside the model. EfficientNetB0 uses "
    "<font face='DJM'>Resizing(96,96)</font> <b>and</b> <font face='DJM'>Rescaling(255.0)</font> (it expects 0&ndash;255, "
    "not 0&ndash;1)."))
A(B("<b>Transfer-learning recipe:</b> <font face='DJM'>VGG16(weights='imagenet', include_top=False)</font> &rarr; "
    "freeze (<font face='DJM'>layer.trainable=False</font> or <font face='DJM'>base.trainable=False</font>) &rarr; "
    "Flatten / GlobalAveragePooling2D &rarr; Dense head with Dropout &rarr; "
    "<font face='DJM'>Adam(learning_rate=0.0001)</font> (lower than the 0.001 used from scratch)."))
A(B("<font face='DJM'>model.evaluate()</font> returns <b>[loss, accuracy] in that order</b> &mdash; "
    "unpack as <font face='DJM'>loss, acc = ...</font>. <font face='DJM'>train</font> generator shuffles; "
    "the test generator must not (<font face='DJM'>shuffle=False</font>)."))

# ---------------- LAB 9 STACKING ----------------
A(H("9 &middot; FDP Day 2 &mdash; stacking three CNNs", ACC2))
A(P("<b>Objective:</b> level-0 = three differently-shaped CNNs on Fashion-MNIST (5 epochs each); "
    "level-1 = a small MLP over their concatenated softmax outputs."))
A(Spacer(1, 1.5))
A(mini_table([
    ["Level-0 model", "Val acc"],
    ["CNN1: 32&rarr;64 conv, Flatten, Dropout .4", "0.8869"],
    ["CNN2: 32-32-64-64 conv, Dropout .25", "<b>0.8906</b>"],
    ["CNN3: 5&times;5 kernel, GAP, Dropout .2/.3", "0.8338"],
    ["<b>Stacked model</b>", "<b>0.9006</b>"],
], [COLW * 0.74, COLW * 0.26]))
A(Spacer(1, 1.5))
A(CB("p1, p2, p3 = cnn1(x), cnn2(x), cnn3(x)     # each (None, 10)\n"
     "merged = Concatenate()([p1, p2, p3])       # -> (None, 30)\n"
     "x = Dense(16, relu)(merged); x = Dropout(0.3)(x)\n"
     "out = Dense(10, softmax)(x)\n"
     "stacking_model = models.Model(inputs=stack_input, outputs=out)\n"
     "cnn1.trainable = cnn2.trainable = cnn3.trainable = False"))
A(Spacer(1, 1.5))
A(B("<b>Why separate generators</b> (<font face='DJM'>train_generator1/2/3</font>): each independently shuffles, "
    "augments and batches, so the three CNNs see different views of the same image."))
A(B("<font face='DJM'>models.Model(inputs=..., outputs=...)</font> does not add a layer &mdash; it packages the "
    "already-connected graph into one trainable model. Freezing the base models means only the meta-learner learns."))
A(B("Stacking beats every base model (0.9006 &gt; 0.8906): the meta-learner learns <i>how much</i> to trust "
    "each CNN, unlike plain soft voting."))

# ---------------- LAB 10 NPTEL ----------------
A(H("10 &middot; NPTEL Week 4 &mdash; VGG16 / VGG19 on Alzheimer MRI", ACC2))
A(P("<b>Objective:</b> compare plain frozen backbones against backbones with extra conv layers. "
    "4 classes, images resized to 128&times;128; <b>4647 train / 744 test</b>."))
A(Spacer(1, 1.5))
A(CB("flow_from_directory(dir, target_size=(128,128),\n"
     "                   class_mode='categorical')   # one-hot -> categorical_crossentropy\n"
     "ImageDataGenerator(rescale=1./255, shear_range=0.4, zoom_range=0.2,\n"
     "  width_shift_range=0.2, height_shift_range=0.2,\n"
     "  rotation_range=90, horizontal_flip=True)"))
A(Spacer(1, 1.5))
A(mini_table([
    ["Variant", "Test acc"],
    ["VGG16, frozen, Dense head only", "77.15%"],
    ["VGG16 + 2&times;Conv2D(128) + BN", "<b>93.55%</b>"],
    ["VGG19, frozen, Dense head only", "73.52%"],
    ["VGG19 + 2&times;Conv2D(256)", "86.29%"],
], [COLW * 0.72, COLW * 0.28]))
A(Spacer(1, 1.5))
A(B("Adding trainable conv layers after the frozen backbone is the big win (+16 pts for VGG16); "
    "the pretrained base is a fixed feature extractor, the new convs adapt to MRI texture."))
A(B("VGG16 beats VGG19 here even though VGG19 is deeper &mdash; more parameters are not automatically better on 4.6k images."))
A(B("<b>Grayscale &rarr; RGB</b> by stacking the channel 3&times;; <font face='DJM'>Dense(4, softmax)</font> because there "
    "are 4 classes &mdash; note the <font face='DJM'>06_07</font> copy reused the same code with "
    "<font face='DJM'>Dense(10)</font> for Fashion-MNIST."))

# ============================== PAGE 3+ ====================================
A(H("Library &amp; function cheat sheet", TEAL))
A(mini_table([
    ["Call", "What it does in <i>our</i> code"],
    ["<font face='DJM'>load_breast_cancer()</font>", "dict-like bunch: .data, .feature_names, .target, .target_names"],
    ["<font face='DJM'>train_test_split</font>", "test_size, random_state, <b>stratify=y</b> keeps class ratio"],
    ["<font face='DJM'>DecisionTreeClassifier</font>", "criterion, max_depth, ccp_alpha, min_samples_split/leaf, random_state"],
    ["<font face='DJM'>cost_complexity_pruning_path</font>", "returns .ccp_alphas / .impurities for pruning sweep"],
    ["<font face='DJM'>plot_tree</font>", "draws tree: filled, rounded, class_names, max_depth"],
    ["<font face='DJM'>GridSearchCV</font>", "param_grid, cv, scoring, n_jobs=-1 &rarr; best_params_/best_score_/best_estimator_"],
    ["<font face='DJM'>RandomizedSearchCV</font>", "param_distributions + <b>n_iter</b> + random_state"],
    ["<font face='DJM'>Pipeline</font>", "named steps; tune with <font face='DJM'>step__param</font> syntax"],
    ["<font face='DJM'>SelectKBest(f_classif)</font>", "keeps k best features by ANOVA F-score; k='all' keeps all"],
    ["<font face='DJM'>StandardScaler / MinMaxScaler</font>", "z=(x&minus;&mu;)/&sigma; vs (x&minus;min)/(max&minus;min); fit on train, transform test"],
    ["<font face='DJM'>VotingClassifier</font>", "voting='hard' (labels) | 'soft' (averaged probabilities), weights="],
    ["<font face='DJM'>SVC</font>", "kernel, C, gamma, decision_function_shape='ovr'"],
    ["<font face='DJM'>GaussianNB / MultinomialNB</font>", "continuous features vs word counts; alpha = Laplace smoothing"],
    ["<font face='DJM'>CountVectorizer / TfidfVectorizer</font>", "min_df, ngram_range, stop_words; fit on train only"],
    ["<font face='DJM'>roc_auc_score / roc_curve</font>", "needs probability scores, not hard labels"],
    ["<font face='DJM'>confusion_matrix(x, y)</font>", "rows = actual, cols = predicted; ConfusionMatrixDisplay plots it"],
    ["<font face='DJM'>accuracy/precision/recall/f1</font>", "average='macro' weights every class equally"],
    ["<font face='DJM'>Sequential / Dense / Conv2D / MaxPooling2D</font>", "KF sequential stack; Conv filters, kernel_size, activation"],
    ["<font face='DJM'>Flatten vs GlobalAveragePooling2D</font>", "vectorises all activations vs averages each feature map"],
    ["<font face='DJM'>ImageDataGenerator.flow / flow_from_directory</font>", "arrays+batch vs folder-per-class with target_size"],
    ["<font face='DJM'>hp.choice / quniform / fmin / tpe.suggest</font>", "Hyperopt: space, discretised ints, search, TPE surrogate"],
    ["<font face='DJM'>optuna study / suggest_*</font>", "direction='maximize', n_trials, best_params"],
], [COLW * 0.42, COLW * 0.58], headbg=TEAL, fs=7.05))
A(Spacer(1, 3))

A(H("Concept revision &mdash; the four formulas that get asked", TEAL))
A(P("<b>Gini</b> 1&minus;&Sigma;p<sub>i</sub><sup>2</sup> &nbsp;|&nbsp; "
    "<b>Entropy</b> &minus;&Sigma;p<sub>i</sub>log<sub>2</sub>p<sub>i</sub> &nbsp;|&nbsp; "
    "<b>Information gain</b> = parent impurity &minus; weighted child impurity"))
A(P("<b>Laplace / add-&alpha;</b> P(w|c) = (count(w,c)+&alpha;) / (&Sigma;<sub>j</sub>count(w<sub>j</sub>,c)+&alpha;V) "
    "&nbsp;&rarr;&nbsp; &alpha;=0 no smoothing, &alpha;=1 standard, &alpha;&rarr;&infin; uniform"))
A(P("<b>Naive Bayes decision</b> c&#770; = argmax<sub>c</sub> [log P(c) + &Sigma;<sub>i</sub> x<sub>i</sub>log P(w<sub>i</sub>|c)] "
    "&nbsp;|&nbsp; <b>SVM objective</b> minimise &frac12;||w||<sup>2</sup> + C&Sigma;&xi;<sub>i</sub>"))
A(Spacer(1, 2))
A(B("<b>Bias&ndash;variance:</b> shallow tree / small C / heavy smoothing = high bias; deep tree / "
    "large C / &alpha;&rarr;0 = high variance."))
A(B("<b>Pre- vs post-pruning:</b> max_depth &amp; min_samples_leaf stop growth early; ccp_alpha penalises "
    "&quot;tree size &times; impurity&quot; after growing it."))
A(B("<b>Filter vs embedded selection:</b> SelectKBest/F-score is a filter outside the model; "
    "<font face='DJM'>feature_importances_</font> is embedded, computed from the fitted tree."))
A(B("<b>Aggregating:</b> bagging = parallel trees on bootstraps (RF); boosting = sequential residual fits "
    "(GradientBoosting); stacking = meta-model on base outputs; voting = fixed rule."))
A(B("<b>Metrics:</b> accuracy favours the majority class; macro-F1 weighs classes equally; AUC ranks "
    "and needs probabilities."))
A(B("<b>Text pipeline:</b> raw text &rarr; CountVectorizer or TfidfVectorizer (tf&middot;idf, L2-normalised) "
    "&rarr; NB. Fit the vectoriser on train only, or the vocabulary leaks."))

A(H("Output &rarr; interpretation", TEAL))
A(mini_table([
    ["You see", "It means"],
    ["<font face='DJM'>[[39,3],[7,65]]</font>", "rows actual: 3 benign called malignant, 7 cancers missed"],
    ["<font face='DJM'>precision .85 recall .93</font>", "few false alarms, catches most positives"],
    ["train 1.00 / test 0.913", "memorising &mdash; overfitting"],
    ["train .92 / test .895", "both low &mdash; underfitting (d=2)"],
    ["CV 0.9385, test 0.9386", "CV estimates test; it does not guarantee it"],
    ["val_acc &gt; train_acc (early)", "augmentation + dropout active only in training"],
    ["105 NaN scores", "invalid hyperparameter &rarr; fits failed"],
    ["&alpha;=0.01 worse than &alpha;=1", "unseen words veto a class"],
], [COLW * 0.40, COLW * 0.60], headbg=TEAL, fs=7.1))
A(Spacer(1, 3))

A(H("MCQ traps checklist", ACCENT))
A(S("<b>Defaults:</b> <font face='DJM'>criterion='gini'</font>, <font face='DJM'>max_depth=None</font>, "
    "<font face='DJM'>ccp_alpha=0.0</font>, <font face='DJM'>n_neighbors=5</font>, "
    "<font face='DJM'>SVC C=1.0, gamma='scale'</font>, <font face='DJM'>MultinomialNB alpha=1.0</font>, "
    "<font face='DJM'>n_estimators=100</font>, <font face='DJM'>max_iter=100</font> (ours used 21)."))
A(S("<b>Names:</b> <font face='DJM'>best_params_</font> (dict), <font face='DJM'>best_score_</font> (CV mean), "
    "<font face='DJM'>best_estimator_</font> (fitted model) &mdash; all end in an underscore."))
A(S("<b>Grid keys:</b> inside a Pipeline the key is <font face='DJM'>'classifier__max_depth'</font> (double underscore) "
    "&mdash; a bare <font face='DJM'>'max_depth'</font> raises an error."))
A(S("<b>Confusion:</b> GridSearchCV = exhaustive; RandomizedSearchCV = "
    "<font face='DJM'>n_iter</font> samples from distributions."))
A(S("<b>Order of returns:</b> <font face='DJM'>evaluate()</font> &rarr; [loss, accuracy]; "
    "<font face='DJM'>train_test_split</font> &rarr; Xtr, Xte, ytr, yte."))
A(S("<b>Shapes:</b> <font face='DJM'>(-1,28,28,1)</font> adds the channel; "
    "<font face='DJM'>predict_proba(X)[:,1]</font> = positive class; "
    "<font face='DJM'>feature_log_prob_</font> is (n_classes, V)."))
A(S("<b>Binary vs multiclass:</b> sigmoid + 1 unit + <font face='DJM'>binary_crossentropy</font> vs softmax "
    "+ n units + <font face='DJM'>categorical</font>/<font face='DJM'>sparse_categorical</font>."))
A(S("<b>Slips:</b> <font face='DJM'>argmax</font> gives an index &rarr; map through "
    "<font face='DJM'>self.classes_</font>; <font face='DJM'>fit_transform</font> train, "
    "<font face='DJM'>transform</font> test; <font face='DJM'>C</font> is <i>inverse</i> regularisation."))
A(Spacer(1, 3))

A(H("Practice exercises &amp; analysis questions in the repo", ACCENT))
A(S("<b>Decision Tree</b> &mdash; 8 reflections: the 63% accuracy floor, Gini vs Entropy, depth peak, "
    "ccp_alpha vs max_depth."))
A(S("<b>Lab 7 NB</b> &mdash; 5 worked reflections: macro-F1 vs accuracy, missing "
    "<font face='DJM'>alpha*V</font>, the two big confusions, &alpha;=0.01 harm, BOC collapse."))
A(S("<b>Week 10 SVM</b> &mdash; 8 written questions: best kernel, boundary shape, wider margin, why soft "
    "margin allows mistakes, which overfits."))
A(Spacer(1, 3))

A(H("Section selector &mdash; what each heading contains", NAVY))
A(mini_table([
    ["Heading / section", "What it is"],
    ["Exploratory Decision Trees", "569&times;30 breast cancer; Gini, depth, ccp_alpha, grid"],
    ["Week4 Lab Solution KNN", "manual vs Grid vs Randomized + voting, 4 UCI datasets"],
    ["Lab7 NaiveBayes SOLUTIONS", "scratch NB, &alpha;, TF-IDF, Bayes Optimal"],
    ["SVM (Week 10)", "linear/rbf/poly kernels, C margins, boundary mesh"],
    ["ML Models &amp; Ensemble", "10 classifiers on ovariantotal.csv"],
    ["HyperParameter Optimization", "Grid / Random / Hyperopt / Optuna, diabetes.csv"],
    ["ANN Hands on Session 1", "Keras Dense 32-32-1, dropout, confusion matrix"],
    ["CNN Sansera / FDP Day 1", "Fashion-MNIST CNN, VGG16, EfficientNet (dupes)"],
    ["FDP Day 2 Stacking", "3 CNNs &rarr; Concatenate &rarr; Dense(16) meta-learner"],
    ["NPTEL Week4 Transfer Learning", "VGG16/19 &plusmn; extra convs, Alzheimer MRI"],
], [COLW * 0.40, COLW * 0.60], headbg=NAVY, fs=7.05))

A(H("Program recognition &mdash; one line &rarr; which lab", ACCENT))
A(mini_table([
    ["Statement / phrase", "Function &rarr; notebook"],
    ["<font face='DJM'>cost_complexity_pruning_path</font>", "pruning &rarr; DT"],
    ["<font face='DJM'>plot_tree(..., filled=True)</font>", "draw tree &rarr; DT"],
    ["<font face='DJM'>itertools.product(*values)</font>", "manual grid &rarr; Week 4"],
    ["<font face='DJM'>n_iter=10</font> + randint", "rand. search &rarr; W4/diabetes"],
    ["<font face='DJM'>SelectKBest(f_classif)</font>", "feature filter &rarr; Week 4"],
    ["<font face='DJM'>alpha * vocabulary_size</font>", "Laplace denominator &rarr; Lab 7 NB"],
    ["<font face='DJM'>X @ feature_log_prob_.T</font>", "vectorised NB scoring &rarr; Lab 7"],
    ["<font face='DJM'>posterior_weights / softmax</font>", "Bayes Optimal &rarr; Lab 7"],
    ["<font face='DJM'>gamma='auto'</font>", "SVM 1/n_features &rarr; Week 10"],
    ["<font face='DJM'>C=0.1 / C=100</font>", "soft vs hard margin &rarr; Week 10"],
    ["<font face='DJM'>np.c_[xx.ravel(), yy.ravel()]</font>", "boundary mesh &rarr; Week 10"],
    ["<font face='DJM'>votes.sum(axis=1) &gt; 2</font>", "manual majority vote &rarr; ML Models"],
    ["<font face='DJM'>GradientBoostingClassifier</font>", "boosting &rarr; ML Models"],
    ["<font face='DJM'>hp.quniform + scope.int</font>", "Hyperopt space &rarr; diabetes"],
    ["<font face='DJM'>loss = -accuracy</font>", "fmin minimises &rarr; diabetes"],
    ["<font face='DJM'>create_study(direction=...)</font>", "Optuna &rarr; diabetes"],
    ["<font face='DJM'>include_top=False</font>", "drop ImageNet head &rarr; transfer labs"],
    ["<font face='DJM'>Dropout(0.2)</font> after dense", "regularised ANN &rarr; ANN"],
    ["<font face='DJM'>Rescaling(255.0)</font>", "EfficientNet input &rarr; CNN"],
    ["<font face='DJM'>Concatenate([x, x, x])</font>", "grey&rarr;RGB &rarr; CNN / NPTEL"],
    ["<font face='DJM'>models.Model(inputs, outputs)</font>", "stacking graph &rarr; FDP Day 2"],
], [COLW * 0.50, COLW * 0.50], headbg=ACCENT, fs=7.05))


# ------------------------------------------------------------------ build ---
OUT = "/home/user/idek/ML_Lab_Quiz_Revision.pdf"

class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        BaseDocTemplate.__init__(self, fn, pagesize=A4, leftMargin=LM,
                                 rightMargin=RM, topMargin=TM, bottomMargin=BM,
                                 title="ML Lab Quiz Revision - 4 pages",
                                 author="Compiled from 120hertzyt-maker/idek",
                                 subject="Revision sheet for the 20-mark ML lab quiz",
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
        canv.drawString(LM, PH - TM + 3.4 * mm,
                        "ML Lab Quiz Revision  ·  idek (main)  ·  compiled from saved notebook outputs")
        canv.drawRightString(PW - RM, PH - TM + 3.4 * mm, "Page %d of 4" % doc.page)
        canv.setStrokeColor(RULE); canv.setLineWidth(0.5)
        canv.line(LM, BM - 3.2 * mm, PW - RM, BM - 3.2 * mm)
        # centre gutter hairline
        canv.setStrokeColor(colors.HexColor("#e3e8ee")); canv.setLineWidth(0.5)
        canv.line(LM + COLW + GUT / 2, BM, LM + COLW + GUT / 2, PH - TM)
        canv.restoreState()

Doc(OUT).build(STORY)
print("built", OUT)

from pypdf import PdfReader
r = PdfReader(OUT)
print("PAGES:", len(r.pages))
