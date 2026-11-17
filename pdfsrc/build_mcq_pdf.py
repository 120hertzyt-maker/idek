#!/usr/bin/env python3
"""MCQ-oriented 4-page revision sheet for the ML lab quiz.

Every value in this document is taken from a *saved* notebook output in
120hertzyt-maker/idek (branch main, commit 27e6a27), or from the notebook's own
stated marking notes. Nothing is invented.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether, Flowable,
                                CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJM", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DJMB", FD + "DejaVuSansMono-Bold.ttf"))
registerFontFamily("DJ", normal="DJ", bold="DJB", italic="DJ", boldItalic="DJB")

INK = colors.HexColor("#14213d")
NAVY = colors.HexColor("#1d3557")
ACCENT = colors.HexColor("#b23a48")
ACC2 = colors.HexColor("#2a6f97")
TEAL = colors.HexColor("#0b6e4f")
GREY = colors.HexColor("#4a4e57")
BG = colors.HexColor("#eef2f7")
RULE = colors.HexColor("#c9d3df")

BODY = ParagraphStyle("body", fontName="DJ", fontSize=9.3, leading=11.9,
                      textColor=INK, spaceAfter=0)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=8.6, leading=11.0)
CODE = ParagraphStyle("code", fontName="DJM", fontSize=7.7, leading=9.6,
                      textColor=colors.HexColor("#16324f"), leftIndent=2.5,
                      spaceBefore=1.2, spaceAfter=1.2, backColor=BG,
                      borderPadding=(1.6, 3, 1.6, 3))
H2 = ParagraphStyle("h2", fontName="DJB", fontSize=10.6, leading=12.4,
                    textColor=colors.white, spaceAfter=0)
H3 = ParagraphStyle("h3", fontName="DJB", fontSize=9.2, leading=11.1,
                    textColor=NAVY, spaceBefore=2.6, spaceAfter=0.8)
TICK = ParagraphStyle("tick", parent=BODY, leftIndent=6.5, bulletIndent=1.2,
                      spaceAfter=0.9)
TICKS = ParagraphStyle("ticks", parent=SMALL, leftIndent=6.5, bulletIndent=1.2,
                       spaceAfter=0.7)
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
    return Paragraph(t, TICK, bulletText="•")


def S(t):
    return Paragraph(t, TICKS, bulletText="–")


def CB(t):
    para = Paragraph(t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                     .replace("\n", "<br/>"), CODE)
    return KeepTogether([para]) if t.count("\n") <= 8 else para


def H(t, color=NAVY):
    tbl = Table([[Paragraph(t, H2)]], colWidths=["100%"])
    tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color),
                             ("LEFTPADDING", (0, 0), (-1, -1), 4),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                             ("TOPPADDING", (0, 0), (-1, -1), 2),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4)]))
    return Pend([CondPageBreak(18 * mm), Spacer(1, 2.5), tbl, Spacer(1, 3.2)])


def h3(t):
    return Paragraph(t, H3)


def T(rows, widths, headbg=NAVY, fs=8.0, zebra=True, maxrows=7):
    """Compact table; cells are mini-markup strings."""
    th = ParagraphStyle("th", fontName="DJB", fontSize=fs, leading=fs + 1.6,
                        textColor=colors.white)
    td = ParagraphStyle("td", fontName="DJ", fontSize=fs, leading=fs + 1.6,
                        textColor=INK)
    data = [[Paragraph(c, th) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(c, td) for c in r])
    def build(chunk):
        t = Table([data[0]] + chunk, colWidths=widths, repeatRows=1)
        st = [("BACKGROUND", (0, 0), (-1, 0), headbg),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("LEFTPADDING", (0, 0), (-1, -1), 2.8),
              ("RIGHTPADDING", (0, 0), (-1, -1), 2.4),
              ("TOPPADDING", (0, 0), (-1, -1), 1.4),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7),
              ("LINEBELOW", (0, 0), (-1, 0), 0.7, headbg),
              ("GRID", (0, 0), (-1, -1), 0.3, RULE)]
        if zebra:
            for i in range(1, len(chunk) + 1):
                if i % 2 == 0:
                    st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f2f5f9")))
        t.setStyle(TableStyle(st))
        return t

    body = data[1:]
    head = list(PEND)
    del PEND[:]
    chunks = [body[i:i + maxrows] for i in range(0, len(body), maxrows)]
    if len(chunks) == 1:
        return (head + [build(chunks[0])]) if head else [build(chunks[0])]
    out = []
    for i, ch in enumerate(chunks):
        blk = build(ch)
        out.append(KeepTogether(head + [blk]) if (i == 0 and head) else KeepTogether([blk]))
    return out


PW, PH = A4
LM = RM = 12.5 * mm
TM = 11.5 * mm
BM = 10.0 * mm
GUT = 6.2 * mm
COLW = (PW - LM - RM - GUT) / 2.0

# ============================ PAGE 1 ======================================
banner = Table([[Paragraph("MCQ Drill Sheet &mdash; ML Labs",
                           ParagraphStyle("bt", fontName="DJB", fontSize=11.8,
                                          leading=13.6, textColor=colors.white))],
                [Paragraph("20 Q &times; 1 mark &middot; 30 min &middot; MCQ only &middot; "
                           "max 2 questions per lab &nbsp;|&nbsp; every value is a saved "
                           "notebook output from this repo",
                           ParagraphStyle("bs", fontName="DJ", fontSize=6.6,
                                          leading=8.3,
                                          textColor=colors.HexColor("#cbd8e8")))]],
               colWidths=[COLW])
banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, 0), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
                            ("TOPPADDING", (0, 1), (-1, 1), 0),
                            ("BOTTOMPADDING", (0, 1), (-1, 1), 4.5)]))
A(banner)
A(Spacer(1, 3.5))
A(P("<b>How to use:</b> §1 predicts outputs, §2 catches shape/return-order traps, §3 kills "
    "look-alike functions, §4 turns parameter changes into answers, §5 separates the concept "
    "twins, §6 is pure one-mark trivia, §7 recognises a program from one line, §8 is the "
    "number bank.", SMALL))
A(Spacer(1, 3))

# ---------------------------------------------------------------- §1 -----
A(H("1 &middot; Snippet &rarr; exact output (highest-yield drill)", ACC2))
A(T([
    ["Code in the repo", "Output / value"],
    ["<font face='DJM'>DecisionTreeClassifier(random_state=42).fit(Xtr,ytr)</font>",
     "<font face='DJM'>get_depth()</font> = <b>7</b>, "
     "<font face='DJM'>get_n_leaves()</font> = <b>19</b>; test acc <b>0.9123</b>"],
    ["<font face='DJM'>len(Xtr), len(Xte)</font> after <font face='DJM'>test_size=0.2</font>",
     "<b>455</b> and <b>114</b>; both <font face='DJM'>(n, 30)</font>"],
    ["<font face='DJM'>confusion_matrix(y_test, baseline_pred)</font>",
     "<font face='DJM'>[[39,3],[7,65]]</font> &rarr; 3 cancers missed, 7 false alarms"],
    ["<font face='DJM'>y.value_counts(normalize=True)</font>",
     "benign <b>0.627</b>, malignant <b>0.373</b> &mdash; a do-nothing model scores 63%"],
    ["<font face='DJM'>grid_search.best_params_</font> / <font face='DJM'>best_score_</font>",
     "<font face='DJM'>{'criterion':'gini','max_depth':4}</font> / <b>0.9385</b> (test 0.9386)"],
    ["<font face='DJM'>depths = range(1,21)</font>; <font face='DJM'>depths[int(np.argmax(test_accs))]</font>",
     "<b>3</b> (0.9386); <font face='DJM'>train_accs[best-1]</font> indexes depth&minus;1"],
    ["<font face='DJM'>path.ccp_alphas[:-1]</font>", "drops the last (largest) alpha &mdash; the trivial single-node tree"],
    ["<font face='DJM'>importance.head(1)</font>", "worst radius <b>0.733548</b> (then worst concave pts 0.1220)"],
    ["<font face='DJM'>train_test_split</font> on wine, <font face='DJM'>test_size=0.3</font>",
     "train <b>(1119, 11)</b> &mdash; 11 features after dropping quality"],
    ["<font face='DJM'>X @ feature_log_prob_.T + class_log_prior_</font>", "shape <font face='DJM'>(n_samples, n_classes)</font>"],
    ["<font face='DJM'>int(STUDENT_ID[-3:])</font> for <font face='DJM'>PES1UG23CS999</font>",
     "<b>999</b> &rarr; <font face='DJM'>SAMPLE_SIZE = 10,999</font>"],
    ["<font face='DJM'>SVC(kernel='rbf', gamma='auto')</font> on moons", "acc <b>0.97</b> (linear 0.87, poly 0.89)"],
    ["<font face='DJM'>Crit[best['criterion']], feat[...], est[...]</font>",
     "<font face='DJM'>gini</font>, <font face='DJM'>sqrt</font>, <font face='DJM'>1300</font> (Hyperopt indices)"],
    ["<font face='DJM'>np.where(pred&gt;0.5,1,0)</font> &rarr; CM (ANN)", "<font face='DJM'>[[32,9],[3,26]]</font> &rarr; <b>0.8286</b>"],
    ["same net + <font face='DJM'>Dropout(0.2)</font> on both hidden layers",
     "<font face='DJM'>[[33,8],[3,26]]</font> &rarr; <b>0.8429</b> (fewer FP)"],
], [COLW * 0.47, COLW * 0.53], headbg=ACC2))
A(Spacer(1, 2.5))

# ---------------------------------------------------------------- §2 -----
A(H("2 &middot; Return-value, order and shape traps", ACCENT))
A(T([
    ["Trap", "The truth"],
    ["<font face='DJM'>model.evaluate(gen)</font>", "returns <b>[loss, accuracy]</b> &mdash; loss first, not accuracy"],
    ["<font face='DJM'>train_test_split</font> order", "<b>X_train, X_test, y_train, y_test</b>"],
    ["<font face='DJM'>confusion_matrix(a, b)</font>", "rows = actual, cols = predicted &mdash; <font face='DJM'>[[TN-like, FN],[FP, TP-like]]</font>"],
    ["<font face='DJM'>predict_proba(X)</font>", "shape <font face='DJM'>(n, n_classes)</font>; <font face='DJM'>[:,1]</font> is the positive class"],
    ["ANN sigmoid output", "<font face='DJM'>model.predict</font> gives <b>(70, 1)</b>, not (70,) &mdash; you threshold yourself"],
    ["<font face='DJM'>print(x)</font> vs <font face='DJM'>return</font>", "most notebook cells <i>print</i>; <font face='DJM'>plot_confusion()</font> also <i>returns</i> <font face='DJM'>cm</font>"],
    ["<font face='DJM'>cm / cm.sum(axis=1, keepdims=True)</font>", "row-normalises: each row shows where that true class went"],
    ["<font face='DJM'>get_depth()</font> / <font face='DJM'>get_n_leaves()</font>", "query methods on a <i>fitted</i> tree, not constructor arguments"],
    ["<font face='DJM'>best_score_</font>", "mean CV score on <i>training</i> folds, not the test score"],
], [COLW * 0.40, COLW * 0.60], headbg=ACCENT))
A(Spacer(1, 2.5))

# ---------------------------------------------------------------- §3 -----
A(H("3 &middot; Look-alike functions &amp; parameters", TEAL))
A(T([
    ["Correct tool", "What the wrong twin does"],
    ["<font face='DJM'>GridSearchCV</font> (every point of <font face='DJM'>param_grid</font>)",
     "<font face='DJM'>RandomizedSearchCV</font> samples <font face='DJM'>n_iter</font> combos from "
     "<font face='DJM'>param_distributions</font>"],
    ["<font face='DJM'>max_depth</font> (stops growth)",
     "<font face='DJM'>ccp_alpha</font> grows the full tree then prunes it"],
    ["<font face='DJM'>cost_complexity_pruning_path()</font> &rarr; <font face='DJM'>.ccp_alphas</font>",
     "passing <font face='DJM'>ccp_alpha=</font> to the constructor (fit-time, no path)"],
    ["<font face='DJM'>feature_importances_</font> (embedded, sums to 1)",
     "<font face='DJM'>SelectKBest(f_classif)</font> &mdash; a filter outside the model"],
    ["<font face='DJM'>Flatten()</font>", "<font face='DJM'>GlobalAveragePooling2D()</font> &mdash; one value per feature map"],
    ["<font face='DJM'>sigmoid</font> + 1 unit + <font face='DJM'>binary_crossentropy</font>",
     "softmax + n units + <font face='DJM'>categorical_crossentropy</font> (one-hot)"],
    ["<font face='DJM'>sparse_categorical_crossentropy</font>", "integer labels; one-hot needs plain <font face='DJM'>categorical</font>"],
    ["<font face='DJM'>fit_transform</font> on train only",
     "<font face='DJM'>fit_transform</font> on test &mdash; refits the scaler, leaks"],
    ["<font face='DJM'>VotingClassifier(voting='soft')</font>",
     "<font face='DJM'>voting='hard'</font> ignores probabilities and any <font face='DJM'>weights=</font>"],
    ["<font face='DJM'>models.Model(inputs, outputs)</font>", "packages a graph; it adds no layer"],
    ["<font face='DJM'>hp.quniform</font> + <font face='DJM'>scope.int</font>", "<font face='DJM'>hp.uniform</font> &mdash; continuous float, never an int"],
    ["<font face='DJM'>RandomState/random_state</font>", "does not change defaults &mdash; only reproducibility"],
], [COLW * 0.47, COLW * 0.53], headbg=TEAL))
A(Spacer(1, 2.5))

# ---------------------------------------------------------------- §4 -----
A(H("4 &middot; Change one parameter &rarr; what happens", NAVY))
A(T([
    ["Change", "Effect seen in our runs"],
    ["<font face='DJM'>criterion</font> gini &rarr; entropy", "same accuracy 0.9123, but depth 7 &rarr; <b>6</b> (different tree)"],
    ["<font face='DJM'>max_depth</font> 1 &rarr; 20", "train &rarr; 1.00, test peaks at <b>d=3</b> then <b>plateaus 0.913</b>"],
    ["<font face='DJM'>ccp_alpha</font> 0 &rarr; large", "0.939 near .003&ndash;.008, then <b>drops to 0.895</b> (underfit)"],
    ["<font face='DJM'>max_depth=None</font> in the grid", "grow until natural stop &mdash; one of the 7 grid values"],
    ["<font face='DJM'>cv=5</font> with 14 combos", "<b>70 fits</b>; <font face='DJM'>cv=10</font> with 75 &rarr; <b>750 fits</b>"],
    ["<font face='DJM'>n_iter</font> 100, cv 3", "<b>300 fits</b>, and 105 failed on <font face='DJM'>max_features='auto'</font>"],
    ["<font face='DJM'>alpha</font> 1.0 &rarr; 0.01 (NB)", "unseen words veto a class; macro-F1 falls most"],
    ["TF-IDF instead of counts, <font face='DJM'>alpha=1.0</font>", "worse (0.5783) &mdash; the pseudo-count swamps L2-normalised values"],
    ["+ <font face='DJM'>ngram_range=(1,2)</font>", "bigrams help with a tuned alpha (0.6632 macro-F1), cost a bigger V"],
    ["<font face='DJM'>C</font> 0.1 &rarr; 100 (SVM)", "softer &rarr; wider margin; harder &rarr; narrow, fits outliers"],
    ["return <b>+</b>accuracy instead of <b>&minus;</b>", "Hyperopt would chase the <i>worst</i> model (&minus;0.95 &lt; &minus;0.80)"],
    ["<font face='DJM'>gamma='auto'</font> vs <font face='DJM'>'scale'</font>", "<font face='DJM'>1/n_features</font> vs <font face='DJM'>1/(n_features&middot;X.var())</font> &mdash; 'scale' is the default"],
], [COLW * 0.42, COLW * 0.58], headbg=NAVY))

# ============================ PAGE 2 ======================================
A(H("5 &middot; Concept twins &mdash; the answer that sounds right but isn't", ACCENT))
A(T([
    ["Pair", "The discriminating line"],
    ["Gini vs Entropy", "1&minus;&Sigma;p<sub>i</sub><sup>2</sup> vs &minus;&Sigma;p<sub>i</sub>log<sub>2</sub>p<sub>i</sub>; both 0 for pure nodes"],
    ["Pre- vs post-pruning", "stop early (<font face='DJM'>max_depth</font>, <font face='DJM'>min_samples_leaf</font>) vs prune after (<font face='DJM'>ccp_alpha</font>)"],
    ["Bagging vs boosting", "parallel bootstraps (RF) vs sequential residual fitting (GradientBoosting)"],
    ["Stacking vs voting", "a <i>learned</i> meta-model on base outputs vs a <i>fixed</i> rule (majority / mean probability)"],
    ["Bagging vs pasting", "sampling with vs without replacement (repo uses RF defaults)"],
    ["Hard vs soft voting", "labels vs averaged <font face='DJM'>predict_proba</font>; soft needs probability support"],
    ["Macro- vs weighted-F1", "equal weight per class vs weight by support &mdash; use macro when rare classes matter"],
    ["Precision vs recall", "TP/(TP+FP) vs TP/(TP+FN); recall = how many real positives you caught"],
    ["Accuracy vs AUC", "thresholded correctness vs ranking quality &mdash; AUC needs scores"],
    ["Stratified vs plain split", "<font face='DJM'>stratify=y</font> keeps the class ratio in both halves"],
    ["Count vs TF-IDF", "raw counts vs tf&middot;idf (L2-normalised, damped common words)"],
    ["Laplace &alpha; small vs large", "trusts counts / vetoed by unseen words vs flattened toward uniform"],
    ["NB 'naive' assumption", "words conditionally <i>independent</i> given the class &mdash; false, yet the argmax survives"],
    ["Kernel trick", "implicit high-dim map so a linear hyperplane curves in the original space"],
    ["BOC vs a plain ensemble", "'optimal' refers to averaging over the <i>true</i> posterior over all hypotheses"],
    ["Bias vs variance", "shallow/small-C/heavy-smoothing vs deep/large-C/&alpha;&rarr;0"],
], [COLW * 0.34, COLW * 0.66], headbg=ACCENT))
A(Spacer(1, 2.5))

A(H("6 &middot; True / false traps (one-mark gold)", TEAL))
A(S("<b>False:</b> deeper trees always improve test accuracy &mdash; depth &gt; 4 only plateaued at 0.913."))
A(S("<b>False:</b> higher <font face='DJM'>ccp_alpha</font> always helps &mdash; past ~0.014 it fell to 0.895."))
A(S("<b>False:</b> trees need feature scaling &mdash; but KNN and SVM do (KNN won with <font face='DJM'>StandardScaler</font>)."))
A(S("<b>False:</b> RandomizedSearchCV is always worse &mdash; here it beat the refined GridSearchCV "
    "(<b>0.8312</b> vs 0.8117)."))
A(S("<b>False:</b> Naive Bayes gives calibrated probabilities &mdash; it is <i>overconfident</i> (correlated words counted twice)."))
A(S("<b>False:</b> a bigger test set removes tuning bias &mdash; the bias comes from <i>selection</i>, not noise."))
A(S("<b>False:</b> the ensemble always beats its best member &mdash; Wine voting 0.7333 &lt; KNN 0.7583; BOC &asymp;0.590 &lt; LR &asymp;0.625."))
A(S("<b>False:</b> the root split is a coincidence &mdash; it acts on 100% of samples, so it usually becomes the #1 importance."))
A(S("<b>True:</b> a wrong NB still classifies &mdash; that is why the lab compares parameters, not accuracy."))
A(S("<b>True:</b> fit the vectoriser on train only, or the vocabulary leaks."))
A(Spacer(1, 2.5))

A(H("7 &middot; Metric &amp; number interpretation", NAVY))
A(T([
    ["You see", "Say this"],
    ["train 1.00 / test 0.913", "<b>overfitting</b>"],
    ["train 0.92 / test 0.895 (d=2)", "<b>underfitting</b> &mdash; both low"],
    ["CV 0.9385, test 0.9386", "CV <i>estimates</i> test; it doesn't guarantee it"],
    ["precision .85 / recall .93", "few false alarms, catches most positives"],
    ["macro-F1 0.66 with acc 0.72", "rare classes drag macro-F1 below accuracy"],
    ["banknote KNN 1.0000", "perfect on this split &mdash; not proof of perfection in general"],
    ["val_acc &gt; train_acc early", "augmentation + dropout act only while training"],
    ["105 NaN scores", "<font face='DJM'>InvalidParameterError</font> &mdash; those fits failed, not zero"],
    ["best loss &minus;0.7655", "accuracy &asymp; <b>0.7655</b> (loss is negated)"],
], [COLW * 0.38, COLW * 0.62], headbg=NAVY))
A(Spacer(1, 2.5))

A(H("8 &middot; Defaults you must be able to quote", ACC2))
A(S("<font face='DJM'>DecisionTreeClassifier</font>: criterion <b>gini</b>, max_depth <b>None</b>, "
    "ccp_alpha <b>0.0</b>, min_samples_split 2, min_samples_leaf 1."))
A(S("<font face='DJM'>KNeighborsClassifier</font>: n_neighbors <b>5</b>, weights <b>uniform</b>, "
    "metric <b>minkowski</b> (p=2 &rarr; euclidean). Ours used 3."))
A(S("<font face='DJM'>SVC</font>: C <b>1.0</b>, kernel <b>rbf</b>, gamma <b>'scale'</b>, degree 3 "
    "(poly), decision_function_shape <b>'ovr'</b>."))
A(S("<font face='DJM'>MultinomialNB</font> / <font face='DJM'>GaussianNB</font>: alpha <b>1.0</b>; "
    "<font face='DJM'>RandomForest</font> n_estimators <b>100</b>; <font face='DJM'>LogisticRegression</font> max_iter <b>100</b> "
    "(ours used 21)."))
A(S("<font face='DJM'>train_test_split</font> test_size 0.25; <font face='DJM'>GridSearchCV</font> cv 5, "
    "<font face='DJM'>scoring=None</font> &rarr; estimator's <font face='DJM'>.score</font>; "
    "<font face='DJM'>CountVectorizer</font> ngram_range <b>(1,1)</b>, min_df <b>1</b>."))
A(S("<font face='DJM'>Dense</font> default activation <b>linear</b>; <font face='DJM'>Adam</font> learning_rate "
    "<b>0.001</b> (labs used 0.0001 for transfer learning)."))
A(S("<font face='DJM'>fmin(max_evals=...)</font> is required; <font face='DJM'>optuna</font> "
    "<font face='DJM'>direction</font> is <b>'minimize'</b> by default."))
A(Spacer(1, 2.5))

A(H("9 &middot; Pipeline &amp; argument-order syntax", TEAL))
A(CB("Pipeline([('scaler', StandardScaler()),\n"
     "          ('feature_selection', SelectKBest(f_classif)),\n"
     "          ('classifier', KNeighborsClassifier())])\n"
     "# tune nested params with a DOUBLE underscore:\n"
     "{'classifier__n_neighbors': [3, 5, 7]}      # not 'n_neighbors'\n"
     "param_grid  -> GridSearchCV   param_distributions -> RandomizedSearchCV\n"
     "VotingClassifier(estimators=[('knn', m1), ('dt', m2)], voting='soft')"))
A(Spacer(1, 1.5))
A(S("<font face='DJM'>SelectKBest(f_classif, k=...)</font> &mdash; <font face='DJM'>'all'</font> keeps everything; "
    "the notebook clamps k to the number of available features."))
A(S("<font face='DJM'>ImageDataGenerator().flow(x, y, batch_size, shuffle=True)</font> for arrays vs "
    "<font face='DJM'>flow_from_directory(dir, target_size, class_mode)</font> for folders "
    "(<font face='DJM'>'categorical'</font> one-hot, <font face='DJM'>'binary'</font> 1-column, "
    "<font face='DJM'>'sparse'</font> integer labels)."))
A(S("<font face='DJM'>model.fit(...)</font> returns a <font face='DJM'>History</font>; metrics live in "
    "<font face='DJM'>history.history['accuracy']</font> / <font face='DJM'>['val_accuracy']</font>. "
    "<font face='DJM'>evaluate(..., verbose=0)</font> returns the list quietly."))

# ============================ PAGE 3 ======================================
A(H("10 &middot; Program recognition &mdash; one line &rarr; which lab", ACC2))
A(T([
    ["Snippet / phrase", "Purpose &rarr; notebook"],
    ["<font face='DJM'>cost_complexity_pruning_path</font>", "pruning sweep &rarr; Decision Tree"],
    ["<font face='DJM'>plot_tree(..., filled=True, rounded=True)</font>", "draw the tree &rarr; Decision Tree"],
    ["<font face='DJM'>x.iloc[:, :10].corr()</font> + <font face='DJM'>sns.heatmap</font>", "correlation EDA &rarr; Decision Tree"],
    ["<font face='DJM'>sns.kdeplot(..., common_norm=False)</font>", "per-class density &rarr; Decision Tree"],
    ["<font face='DJM'>itertools.product(*values)</font>", "manual grid &rarr; Week 4"],
    ["<font face='DJM'>best_score = -1; if mean_auc &gt; best_score</font>", "manual argmax &rarr; Week 4"],
    ["<font face='DJM'>SelectKBest(f_classif)</font>", "ANOVA filter &rarr; Week 4"],
    ["<font face='DJM'>np.mean(votes) &gt; 0.5</font>", "manual soft vote &rarr; Week 4"],
    ["<font face='DJM'>alpha * vocabulary_size</font>", "Laplace denominator &rarr; Lab 7 NB"],
    ["<font face='DJM'>self.classes_[np.argmax(scores, axis=1)]</font>", "vectorised NB predict &rarr; Lab 7"],
    ["<font face='DJM'>weights=list(posterior_weights)</font>", "Bayes Optimal vote &rarr; Lab 7"],
    ["<font face='DJM'>grid.fit(X_dev, y_dev)</font> then refit on train", "dev-tuned, test scored once &rarr; Lab 7"],
    ["<font face='DJM'>gamma='auto'</font>", "<font face='DJM'>1/n_features</font> &rarr; Week 10 SVM"],
    ["<font face='DJM'>C=0.1</font> vs <font face='DJM'>C=100</font>", "soft vs hard margin &rarr; Week 10"],
    ["<font face='DJM'>np.c_[xx.ravel(), yy.ravel()]</font> + <font face='DJM'>contourf</font>", "boundary mesh &rarr; Week 10"],
    ["<font face='DJM'>np.column_stack(...)</font> + <font face='DJM'>votes.sum(axis=1) &gt; 2</font>", "majority vote &rarr; ML Models"],
    ["<font face='DJM'>GradientBoostingClassifier</font>", "boosting (chart says XGBoost) &rarr; ML Models"],
    ["<font face='DJM'>GaussianNB()</font>", "continuous features &rarr; ML Models"],
    ["<font face='DJM'>hp.choice / quniform / fmin / tpe.suggest</font>", "Hyperopt space &rarr; diabetes"],
    ["<font face='DJM'>loss = -accuracy</font>", "<font face='DJM'>fmin</font> minimises &rarr; diabetes"],
    ["<font face='DJM'>create_study(direction='maximize')</font>", "Optuna &rarr; diabetes"],
    ["<font face='DJM'>Dense(32, relu, input_dim=49)</font>", "first ANN &rarr; ANN session"],
    ["<font face='DJM'>reshape(-1, 28, 28, 1)</font>", "add channel axis &rarr; CNN"],
    ["<font face='DJM'>Rescaling(255.0)</font>", "EfficientNet expects 0&ndash;255 &rarr; CNN"],
    ["<font face='DJM'>Concatenate()([x, x, x])</font>", "grey &rarr; RGB &rarr; CNN / NPTEL"],
    ["<font face='DJM'>include_top=False</font> + freeze", "feature extractor &rarr; all transfer labs"],
    ["<font face='DJM'>Concatenate()([p1, p2, p3])</font> + <font face='DJM'>Dense(16)</font>", "stacking meta-learner &rarr; FDP Day 2"],
    ["<font face='DJM'>flow_from_directory(class_mode='categorical')</font>", "4-class MRI &rarr; NPTEL"],
], [COLW * 0.55, COLW * 0.45], headbg=ACC2, fs=7.8, maxrows=3))
A(Spacer(1, 2.5))

# --------------------------------------------------------------- §11 -----
A(H("11 &middot; Number bank (memorise the bold ones)", TEAL))
A(T([
    ["Lab", "Saved results"],
    ["Decision Tree", "baseline <b>0.9123</b> (d7, 19 leaves); best depth <b>3</b> &rarr; 0.9386; grid gini/d4 &rarr; <b>0.9386</b>; CV 0.9385"],
    ["Week 4", "Wine DT 0.7229 / KNN <b>0.7583</b>; Banknote DT 0.9927 / KNN <b>1.0000</b>; QSAR DT 0.7666 / KNN <b>0.8517</b>; HR skipped"],
    ["Lab 7 NB", "counts <b>0.7226</b> / 0.6567; untuned TF-IDF 0.6950 / 0.5783; tuned bigrams <b>0.7416</b> / 0.6632; best &alpha; on dev 1.0"],
    ["Week 10 SVM", "moons .87 / <b>.97</b> / .89; banknote .88 / <b>.93</b> / .84 (linear/RBF/poly)"],
    ["ML Models", "LR <b>0.8977</b>; SVM-lin 0.8750; NB 0.8523; RF 0.8523; GB 0.8523; KNN 0.8409; DT 0.8182; RBF 0.7955; sigmoid 0.7841; poly 0.6705; vote <b>0.8750</b>"],
    ["HPO", "baseline 0.7922; manual 0.8247; random <b>0.8312</b>; grid 0.8117; hyperopt 0.8117"],
    ["ANN", "no dropout <b>0.8286</b>; with dropout <b>0.8429</b>"],
    ["CNN", "scratch <b>0.8625</b>; VGG16 0.8854; EfficientNetB0 <b>0.8926</b>"],
    ["Stacking", "CNN1 .8869 / CNN2 <b>.8906</b> / CNN3 .8338 &rarr; stacked <b>0.9006</b>"],
    ["NPTEL", "VGG16 <b>77.15%</b>; VGG16+2conv <b>93.55%</b>; VGG19 73.52%; VGG19+2conv 86.29%"],
], [COLW * 0.22, COLW * 0.78], headbg=TEAL, fs=7.7, maxrows=4))
A(Spacer(1, 2.5))

A(H("12 &middot; Datasets &amp; shapes", NAVY))
A(T([
    ["Dataset", "Shape / target"],
    ["Breast cancer", "569&times;30, 0 malignant 212 / 1 benign 357"],
    ["PubMed RCT", "180,040 train sentences, 5 roles"],
    ["Ovarian", "349&times;50, TYPE, 49 features &rarr; 88 test rows"],
    ["Diabetes", "768&times;9, Outcome 500 / 268"],
    ["Wine", "1599&times;12 &rarr; good_quality = quality &gt; 5"],
    ["Banknote", "1372&times;5 (4 features); SVM uses only variance + skewness"],
    ["Fashion-MNIST", "60,000 &times; 28&times;28 train, 10,000 test, 10 classes"],
    ["Alzheimer (NPTEL)", "4647 train / 744 test &times; 128&times;128, 4 classes"],
], [COLW * 0.40, COLW * 0.60], headbg=NAVY, fs=7.7, maxrows=4))

# ============================ PAGE 4 ======================================
A(H("13 &middot; Compute it yourself &mdash; shapes and metrics", ACCENT))
A(P("<i>Derived from the code, not printed in the notebooks &mdash; but standard Keras/sklearn arithmetic. "
    "Examiners love these.</i>", SMALL))
A(Spacer(1, 1.5))
A(T([
    ["Question", "Worked answer"],
    ["Conv2D(32,(3,3)) on 28&times;28, <b>no padding</b>",
     "28&minus;3+1 = <b>26</b>; then MaxPool 2&rarr;13, Conv&rarr;11, pool&rarr;<b>5</b>, Conv&rarr;3, pool&rarr;<b>1</b>"],
    ["...so <font face='DJM'>Flatten()</font> gives", "128&times;1&times;1 = <b>128</b> features into <font face='DJM'>Dense(128)</font>"],
    ["Same stack with <font face='DJM'>padding='same'</font> (Day 2)", "28&rarr;28, pool&rarr;14, 14&rarr;14, pool&rarr;7 &rarr; Flatten <b>64&times;7&times;7 = 3136</b>"],
    ["<font face='DJM'>GlobalAveragePooling2D()</font> after 128 filters", "one value per map &rarr; a <b>128</b>-vector (no 7&times;7)"],
    ["accuracy from <font face='DJM'>[[39,3],[7,65]]</font>", "(39+65)/<b>114</b> = <b>0.9123</b>; malignant recall 39/42 = 0.93, precision 39/46 = 0.85"],
    ["accuracy from <font face='DJM'>[[39,3],[4,68]]</font>", "(39+68)/114 = <b>0.9386</b> &mdash; the grid-search model"],
    ["accuracy from <font face='DJM'>[[38,6],[5,39]]</font>", "(38+39)/<b>88</b> = <b>0.875</b> &mdash; the voting ensemble"],
    ["accuracy from <font face='DJM'>[[32,9],[3,26]]</font>", "(32+26)/<b>70</b> = <b>0.8286</b> &mdash; ANN, 20% of 349"],
], [COLW * 0.42, COLW * 0.58], headbg=ACCENT, fs=7.6))
A(Spacer(1, 2.5))

A(H("14 &middot; Distractor patterns per lab", NAVY))
A(T([
    ["Lab", "The option that is designed to tempt you"],
    ["Decision Tree", "'entropy always beats gini' (here 0.9123 both) &middot; 'deeper = better' &middot; "
     "'accuracy alone tells the story' &middot; 'ccp_alpha stops the tree growing'"],
    ["Week 4", "'manual search = GridSearchCV results, so it is just code style' "
     "(same winners, but manual loops over <font face='DJM'>itertools.product</font>) &middot; "
     "'KNN needs no scaling' &middot; 'voting always wins'"],
    ["Lab 7 NB", "'more smoothing, better accuracy' &middot; 'TF-IDF is always better than counts' &middot; "
     "'BOC must beat its members' &middot; 'tune on test, it is bigger'"],
    ["Week 10 SVM", "'linear kernel handles moons' &middot; 'C=100 gives a wider margin' &middot; "
     "'RBF is linear in a higher dimension' (it is <i>implicit</i>) &middot; 'poly always overfits'"],
    ["ML Models", "'XGBoost was trained' (it was GradientBoosting) &middot; 'poly kernel is best because "
     "it is most flexible' (0.6705, worst) &middot; 'SVC sigmoid = logistic regression'"],
    ["HPO", "'RandomizedSearchCV is a subset of the grid, so it is always worse' &middot; "
     "'Optuna needs a surrogate you define' (it builds one) &middot; "
     "'<font face='DJM'>max_features='auto'</font> is the default' (removed)"],
    ["Keras labs", "'<font face='DJM'>Dense(1, relu)</font> for binary' &middot; "
     "'<font face='DJM'>evaluate</font> returns accuracy first' &middot; "
     "'augment the test set too' &middot; '<font face='DJM'>Flatten</font> and <font face='DJM'>GAP</font> are interchangeable'"],
], [COLW * 0.20, COLW * 0.80], headbg=NAVY, fs=7.6))
A(Spacer(1, 2.5))

A(H("15 &middot; Exam-technique for tricky MCQs", ACCENT))
A(S("<b>Two options differ only by a number</b> &rarr; decide: is it a default, a saved result, or a derived "
    "quantity? Only the first two are memorisable; derived ones (Conv2D sizes) must be computed."))
A(S("<b>&quot;Returns&quot; vs &quot;prints&quot;</b> &rarr; the notebook's wording decides: "
    "<font face='DJM'>accuracy_score</font> returns a float, the cell prints it."))
A(S("<b>&quot;Prevents overfitting&quot;</b> &rarr; ask if it acts during fitting "
    "(<font face='DJM'>max_depth</font>, dropout, early stopping) or afterwards "
    "(<font face='DJM'>ccp_alpha</font>)."))
A(S("<b>&quot;Why did X score higher&quot;</b> &rarr; prefer the mechanical cause (scaling, leakage, selection bias, "
    "imbalance) over &quot;better algorithm&quot;."))
A(S("<b>Anchors</b>: tabular 0.79&ndash;0.94; text macro-F1 0.58&ndash;0.66; images 0.86&ndash;0.90; "
    "differences &lt; 0.01 are noise."))
A(S("<b>A &quot;better&quot; model that used the test set for tuning</b> is not better &mdash; the score is "
    "optimistic, so prefer the option that names leakage over the one that names the algorithm."))
A(S("<b>A numbers-only distractor</b> is usually off by a shape (455/114 vs 569), a sign (loss "
    "&minus;0.95) or a factor of 10 (0.8286 vs 82.86)."))
A(S("<b>&quot;Always / never&quot;</b> options usually lose: scaling, deeper trees, more smoothing and bigger "
    "test splits each fail somewhere in this repo."))
A(Spacer(1, 2.5))

A(H("16 &middot; Where the repo gives no evidence (do not guess numbers)", TEAL))
A(S("<b>HR Attrition</b> never ran &mdash; <font face='DJM'>FileNotFoundError</font>, pipeline skipped the dataset. No metrics exist."))
A(S("<b>Lab 7 Part C</b> depends on the student's SRN (<font face='DJM'>SAMPLE_SIZE = 10,000 + last three digits</font>). "
    "Only the <i>ordering</i> is fixed: LR &asymp;0.625 &gt; BOC &asymp;0.590 &gt; NB &asymp;0.549 &gt; RF &asymp;0.409 &gt; DT &asymp;0.346."))
A(S("<b>No outputs</b> in: all of Lab 7's code cells (instructor copy &mdash; its figures are from the marking notes), "
    "the FDP &quot;own dataset&quot; block, the <font face='DJM'>pip install optuna</font> cell, and the Optuna "
    "<font face='DJM'>best_params</font> / <font face='DJM'>trial</font> cells."))
A(S("<b>Numbers that look computed but are hard-coded</b>: the ML Models bar charts (e.g. the &quot;XGBoost&quot; bar) &mdash; "
    "the model actually trained is <font face='DJM'>GradientBoostingClassifier</font>."))
A(Spacer(1, 2.5))

A(H("17 &middot; Rapid-fire drill &mdash; likely stem, correct choice", ACC2))
A(P("<i>Cover the right column; the tempting wrong options are in §14.</i>", SMALL))
A(T([
    ["Stem", "Answer"],
    ["Which argument makes a tree stop early?", "<font face='DJM'>max_depth</font> (or <font face='DJM'>min_samples_leaf</font>)"],
    ["Which argument prunes a tree after it is grown?", "<font face='DJM'>ccp_alpha</font>"],
    ["Which function returns the alpha values worth testing?", "<font face='DJM'>cost_complexity_pruning_path()</font>"],
    ["Which NB variant suits word counts?", "<font face='DJM'>MultinomialNB</font> (<font face='DJM'>GaussianNB</font> for continuous)"],
    ["What does &alpha;V keep valid?", "the smoothed word distribution (sums to 1)"],
    ["Which kernel for a circular boundary?", "<font face='DJM'>'rbf'</font>"],
    ["What does a large C do to the margin?", "narrows it (less regularisation)"],
    ["Which Hyperopt function runs the search?", "<font face='DJM'>fmin</font>"],
    ["Which loss for integer class labels?", "<font face='DJM'>sparse_categorical_crossentropy</font>"],
    ["Which flag drops ImageNet's classifier?", "<font face='DJM'>include_top=False</font>"],
    ["Which call makes a backbone a frozen extractor?", "<font face='DJM'>layer.trainable = False</font>"],
], [COLW * 0.55, COLW * 0.45], headbg=ACC2, fs=7.5))
A(Spacer(1, 2.5))

A(H("18 &middot; Ten-second self-test", ACC2))
A(P("<b>Cover the answers.</b> (1) Default criterion? <i>gini</i>. (2) Which returns loss first? <i>evaluate</i>. "
    "(3) Best depth on breast cancer? <i>3</i>. (4) What does <font face='DJM'>alpha</font> multiply in the "
    "denominator? <i>vocabulary size</i>. (5) Which kernel wins on moons? <i>RBF</i>. (6) <font face='DJM'>C=0.1</font> "
    "gives a wider or narrower margin? <i>wider</i>. (7) Which search samples n_iter combos? <i>RandomizedSearchCV</i>. "
    "(8) Sign of the Hyperopt loss? <i>minus accuracy</i>. (9) Stacked model accuracy? <i>0.9006</i>. "
    "(10) Which transfer model won on Fashion-MNIST? <i>EfficientNetB0, 0.8926</i>.", SMALL))
A(Spacer(1, 3))

A(H("19 &middot; Real quirks in these notebooks (fair game for 'which is true')", TEAL))
A(P("<b>ANN:</b> a <font face='DJM'>StandardScaler</font> is built and printed, but training uses the "
    "<font face='DJM'>MinMaxScaler</font> output <font face='DJM'>X_scale</font>. &nbsp;<b>ML Models:</b> both bar "
    "charts take literal lists; the second is labelled &quot;XGBoost&quot; while the trained model is "
    "<font face='DJM'>GradientBoostingClassifier</font>. &nbsp;<b>Week 4:</b> "
    "<font face='DJM'>feature_selection__k</font> is clamped to the feature count (banknote &rarr; <b>4</b>, not 8); "
    "<font face='DJM'>evaluate_models</font> pulls <font face='DJM'>X_train/y_train</font> from "
    "<font face='DJM'>global</font>. &nbsp;<b>Lab 7:</b> Part C uses <font face='DJM'>X_train[:SAMPLE_SIZE]</font> "
    "(first N rows, not a random sample); the grid is fitted on <font face='DJM'>X_dev</font>, then refit on "
    "<font face='DJM'>X_train</font>. &nbsp;<b>SVM:</b> the text claims a high-dimensional multi-class problem, but "
    "part 3 uses <font face='DJM'>make_blobs(centers=2)</font> plus 2 outliers. &nbsp;<b>CNN:</b> the head is "
    "<font face='DJM'>Dense(10, softmax)</font> while the comment still says &quot;4 classes&quot;. "
    "&nbsp;<b>NPTEL:</b> the &quot;+2 conv&quot; variants keep <font face='DJM'>Flatten</font>. "
    "&nbsp;<b>Duplicate:</b> the two CNN notebooks are identical (10 distinct labs).", SMALL))
A(Spacer(1, 1.5))

A(P("<b>Provenance.</b> All 11 notebooks in <font face='DJM'>120hertzyt-maker/idek</font> @ "
    "<font face='DJM'>27e6a27</font>. Not re-executed: each figure is a saved output or a repo marking note.", SMALL))
A(Spacer(1, 2))

# ------------------------------------------------------------------ build --
OUT = "/home/user/idek/ML_Lab_Quiz_MCQ_Revision.pdf"


class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        BaseDocTemplate.__init__(self, fn, pagesize=A4, leftMargin=LM,
                                 rightMargin=RM, topMargin=TM, bottomMargin=BM,
                                 title="ML Lab Quiz - MCQ Drill Sheet (4 pages)",
                                 author="Compiled from 120hertzyt-maker/idek",
                                 subject="MCQ-oriented revision for a 20-question, 1-mark quiz",
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
                        "ML Lab Quiz \u00b7 MCQ drill sheet \u00b7 idek (main, 27e6a27)")
        canv.drawRightString(PW - RM, PH - TM + 3.4 * mm, "Page %d of 4" % doc.page)
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(LM, BM - 3.2 * mm, PW - RM, BM - 3.2 * mm)
        canv.setStrokeColor(colors.HexColor("#e3e8ee"))
        canv.line(LM + COLW + GUT / 2, BM, LM + COLW + GUT / 2, PH - TM)
        canv.restoreState()


Doc(OUT).build(STORY)
print("built", OUT)

from pypdf import PdfReader
print("PAGES:", len(PdfReader(OUT).pages))
