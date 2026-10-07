"""Part A: the eight assignment problems, as handwriting sheets.

Block forms (build.py wraps every prose block to the ruled line):
    ("q",    "Problem 3.4")             problem heading
    ("stmt", "full textbook statement") blue, the shared preamble
    ("part", "(a) question text")       blue, one sub-question
    ("ans",  "text")                    first answer paragraph, opens "Answer:"
    ("p",    "text")                    answer paragraph
    ("li",   "1. text")                 numbered or bulleted item
    ("sub",  "Scan 1")                  small heading inside an answer
    ("math", "x = 1")                   one monospace line, never wrapped
    ("table", heads, rows, align, marks) marks = {row_index: "ok"|"no"|"key"}
    ("svg",  name)                      a drawn diagram from diagrams.py
    ("blank",)                          one empty ruled line
    ("h",    "Problem 6.7, continued")  heading repeated at a page break
"""

BLOCKS = [

# =========================================================== 3.4
("q", "Problem 3.4"),
("stmt", "Suppose that a data warehouse consists of the three dimensions "
         "time, doctor, and patient, and the two measures count and charge, "
         "where charge is the fee that a doctor charges a patient for a visit."),
("part", "(a) Enumerate three classes of schemas that are popularly used "
         "for modeling data warehouses."),
("ans", "The three schema classes are:"),
("li", "1. Star schema. One central fact table holds the measures and one "
       "foreign key per dimension. Each dimension is a single table."),
("li", "2. Snowflake schema. A star schema in which some dimension tables "
       "are normalised into smaller tables, giving a snowflake shape."),
("li", "3. Fact constellation, also called a galaxy schema. Several fact "
       "tables share the same dimension tables."),
("blank",),
("part", "(b) Draw a schema diagram for the above data warehouse using one "
         "of the schema classes listed in (a)."),
("ans", "A star schema. The fact table fee holds the measures count and "
        "charge and one key for each of the three dimensions."),
("svg", "star_doctor"),
("blank",),
("part", "(c) Starting with the base cuboid [day, doctor, patient], what "
         "specific OLAP operations should be performed in order to list the "
         "total fee collected by each doctor in 2010?"),
("ans", "Three operations, in this order:"),
("li", "1. Roll-up on time from day to year, so each cell sums the charge "
       "of a whole year."),
("li", "2. Slice on time with year = 2010."),
("li", "3. Roll-up on patient from individual patient to all, so the "
       "charge is summed over every patient."),
("p", "The result is the cuboid [2010, doctor, all]. Each cell holds "
      "sum(charge), the total fee collected by one doctor in 2010."),

# =========================================================== 3.5
("q", "Problem 3.5"),
("stmt", "Suppose that a data warehouse for Big_University consists of the "
         "four dimensions student, course, semester, and instructor, and two "
         "measures count and avg_grade. At the lowest conceptual level (e.g., "
         "for a given student, course, semester, and instructor combination), the "
         "avg_grade measure stores the actual course grade of the student. "
         "At higher conceptual levels, avg_grade stores the average grade "
         "for the given combination."),
("part", "(a) Draw a snowflake schema diagram for the data warehouse."),
("ans", "The fact table university holds count and avg_grade. Student, "
        "course and instructor are normalised: student points to major, and "
        "course and instructor both point to department."),
("svg", "snowflake_university"),
("blank",),
("part", "(b) Starting with the base cuboid [student, course, semester, "
         "instructor], what specific OLAP operations (e.g., roll-up from "
         "semester to year) should you perform in order to list the average "
         "grade of CS courses for each Big_University student."),
("ans", "Four operations, in this order:"),
("li", "1. Roll-up on course from course_id to department."),
("li", "2. Roll-up on semester to all, and on instructor to all."),
("li", "3. Dice on department = \"CS\" and university = \"Big_University\"."),
("li", "4. Keep student at the student level, so there is one row per "
       "student."),
("p", "The result is [student, CS, all, all], holding the average CS grade "
      "of each Big_University student."),
("p", "avg_grade is an algebraic measure. To roll it up, keep sum(grade) "
      "and count, then divide. An average of averages gives a wrong answer."),
("blank",),
("part", "(c) If each dimension has five levels (including all), such as "
         "\"student < major < status < university < all,\" how many cuboids "
         "will this cube contain (including the base and apex cuboids)?"),
("ans", "Each dimension can be taken at any one of its five levels, so the "
        "number of cuboids is the product of the level counts:"),
("math", "cuboids = 5 x 5 x 5 x 5 = 5^4 = 625"),
("p", "The cube contains 625 cuboids. This count already includes the base "
      "cuboid and the apex cuboid."),

# =========================================================== 3.6
("q", "Problem 3.6"),
("stmt", "Suppose that a data warehouse consists of the four dimensions "
         "date, spectator, location, and game, and the two measures count and "
         "charge, where charge is the fare that a spectator pays when "
         "watching a game on a given date. Spectators may be students, adults, "
         "or seniors, with each category having its own charge rate."),
("part", "(a) Draw a star schema diagram for the data warehouse."),
("ans", "The fact table sales holds count and charge and one key per "
        "dimension. The spectator table carries category, which decides the "
        "charge rate."),
("svg", "star_spectator"),
("blank",),
("part", "(b) Starting with the base cuboid [date, spectator, location, "
         "game], what specific OLAP operations should you perform in order "
         "to list the total charge paid by student spectators at GM_Place "
         "in 2010?"),
("ans", "Four operations, in this order:"),
("li", "1. Roll-up on date from day to year."),
("li", "2. Roll-up on spectator from spectator_id to category."),
("li", "3. Roll-up on game to all."),
("li", "4. Dice on year = 2010, category = \"student\" and location_name = "
       "\"GM_Place\"."),
("p", "One cell is left. It holds sum(charge), the total charge paid by "
      "student spectators at GM_Place in 2010."),

# =========================================================== 4.6 (a)
("q", "Problem 4.6 (a)"),
("stmt", "A database has five transactions. Let min_sup = 60% and "
         "min_conf = 80%."),
("table", ["TID", "items_bought"],
 [["T100", "{M, O, N, K, E, Y}"],
  ["T200", "{D, O, N, K, E, Y}"],
  ["T300", "{M, A, K, E}"],
  ["T400", "{M, U, C, K, Y}"],
  ["T500", "{C, O, O, K, I, E}"]], "ll", {}),
("part", "(a) Find all frequent itemsets using Apriori and FP-growth, "
         "respectively. Compare the efficiency of the two mining processes."),
("ans", "min_sup = 60% of 5 transactions, so an itemset is frequent when "
        "its count is at least 3."),
("math", "minimum count = 0.6 x 5 = 3"),
("blank",),
("sub", "Apriori, scan 1: count each item (C1)"),
("p", "T500 holds O twice, but it counts once for that transaction."),
("table", ["item", "count", "item", "count"],
 [["K", "5", "N", "2"],
  ["E", "4", "C", "2"],
  ["M", "3", "D", "1"],
  ["O", "3", "A", "1"],
  ["Y", "3", "U, I", "1 each"]], "lrlr", {}),
("math", "L1 = {K}:5 {E}:4 {M}:3 {O}:3 {Y}:3"),
("blank",),
("sub", "Apriori, scan 2: count the 10 pairs of L1 (C2)"),
("table", ["pair", "count", "frequent?"],
 [["{K, E}", "4", "yes"],
  ["{K, M}", "3", "yes"],
  ["{K, O}", "3", "yes"],
  ["{K, Y}", "3", "yes"],
  ["{E, O}", "3", "yes"],
  ["{E, M}", "2", "no"],
  ["{E, Y}", "2", "no"],
  ["{M, Y}", "2", "no"],
  ["{O, Y}", "2", "no"],
  ["{M, O}", "1", "no"]], "lrl",
 {0: "ok", 1: "ok", 2: "ok", 3: "ok", 4: "ok", 5: "no", 6: "no", 7: "no",
  8: "no", 9: "no"}),
("math", "L2 = {K,E}:4 {K,M}:3 {K,O}:3 {K,Y}:3 {E,O}:3"),
("blank",),
("sub", "Apriori, scan 3: join L2, then prune (C3)"),
("p", "Join pairs of L2 that share their first item. Prune a candidate if "
      "any 2-item subset is missing from L2."),
("table", ["candidate", "infrequent subset", "result"],
 [["{E, K, O}", "none", "keep, count 3"],
  ["{K, M, O}", "{M, O}", "pruned"],
  ["{K, M, Y}", "{M, Y}", "pruned"],
  ["{K, O, Y}", "{O, Y}", "pruned"]], "lll",
 {0: "ok", 1: "no", 2: "no", 3: "no"}),
("p", "{E, K, O} occurs in T100, T200 and T500, so its count is 3."),
("math", "L3 = {E,K,O}:3"),
("p", "One 3-itemset cannot be joined into a 4-itemset, so C4 is empty and "
      "Apriori stops after three scans."),
("blank",),
("sub", "Frequent itemsets (both methods give these 11)"),
("table", ["size", "frequent itemsets with counts"],
 [["1", "K:5, E:4, M:3, O:3, Y:3"],
  ["2", "KE:4, KM:3, KO:3, KY:3, EO:3"],
  ["3", "EKO:3"]], "ll", {0: "key", 1: "key", 2: "key"}),
("blank",),
("sub", "FP-growth, scan 1: order the frequent items"),
("p", "Sort the items of L1 by falling count. Ties keep the order K, E, M, "
      "O, Y."),
("math", "order: K:5, E:4, M:3, O:3, Y:3"),
("sub", "FP-growth, scan 2: insert each transaction"),
("p", "Drop the infrequent items from each transaction, sort the rest in "
      "that order, and insert the path into the tree."),
("table", ["TID", "ordered frequent items"],
 [["T100", "K, E, M, O, Y"],
  ["T200", "K, E, O, Y"],
  ["T300", "K, E, M"],
  ["T400", "K, M, Y"],
  ["T500", "K, E, O"]], "ll", {}),
("blank",),
("p", "The FP-tree with its header table. Each node shows item:count."),
("svg", "fp_tree"),
("blank",),
("sub", "FP-growth: mine each item, bottom of header first"),
("table", ["item", "conditional pattern base", "frequent patterns"],
 [["Y", "{K,E,M,O}:1 {K,E,O}:1 {K,M}:1", "{K,Y}:3"],
  ["O", "{K,E,M}:1 {K,E}:2", "{K,O}:3 {E,O}:3 {K,E,O}:3"],
  ["M", "{K,E}:2 {K}:1", "{K,M}:3"],
  ["E", "{K}:4", "{K,E}:4"]], "lll", {0: "key", 1: "key", 2: "key", 3: "key"}),
("p", "In the base of Y, only K reaches count 3, so Y gives {K,Y} alone. In "
      "the base of O, both K and E reach 3, so O gives three patterns."),
("blank",),
("sub", "Comparing the efficiency"),
("li", "1. Apriori scanned the database three times, once per itemset size. "
       "FP-growth scanned it twice."),
("li", "2. Apriori generated 10 candidate pairs and 4 candidate triples, and "
       "8 of these 14 were not frequent. FP-growth generates no candidates."),
("li", "3. FP-growth mines the compact tree in memory, by building smaller "
       "conditional trees. It is the more efficient of the two."),

# =========================================================== 6.7
("q", "Problem 6.7"),
("stmt", "The following table consists of training data from an employee "
         "database. The data have been generalized. For example, \"31...35\" "
         "for age represents the age range of 31 to 35. For a given row "
         "entry, count represents the number of data tuples having the "
         "values for department, status, age, and salary given in that row. "
         "Let status be the class label attribute."),
("table", ["department", "status", "age", "salary", "count"],
 [["sales", "senior", "31...35", "46K...50K", "30"],
  ["sales", "junior", "26...30", "26K...30K", "40"],
  ["sales", "junior", "31...35", "31K...35K", "40"],
  ["systems", "junior", "21...25", "46K...50K", "20"],
  ["systems", "senior", "31...35", "66K...70K", "5"],
  ["systems", "junior", "26...30", "46K...50K", "3"],
  ["systems", "senior", "41...45", "66K...70K", "3"],
  ["marketing", "senior", "36...40", "46K...50K", "10"],
  ["marketing", "junior", "31...35", "41K...45K", "4"],
  ["secretary", "senior", "46...50", "36K...40K", "4"],
  ["secretary", "junior", "26...30", "26K...30K", "6"]], "llllr", {}),
("part", "(a) How would you modify the basic decision tree algorithm to take "
         "into consideration the count of each generalized data tuple (i.e., "
         "of each row entry)?"),
("ans", "Each row stands for count identical tuples. Wherever the basic "
        "algorithm adds 1 for a tuple, add that row's count instead:"),
("li", "1. |D| is the sum of the counts, not the number of rows."),
("li", "2. The size of class Ci is the sum of counts of the rows in Ci."),
("li", "3. Info(D), Info_A(D), SplitInfo and Gini all use these weighted "
       "sizes."),
("li", "4. Majority voting at a leaf compares summed counts."),
("p", "Totals for this table:"),
("math", "|D| = 165,  senior = 52,  junior = 113"),
("blank",),
("part", "(b) Use your algorithm to construct a decision tree from the "
         "given data."),
("ans", "Use information gain. First the expected information of D:"),
("math", "Info(D) = -(52/165)log2(52/165)"),
("math", "          -(113/165)log2(113/165)"),
("math", "        = 0.5250 + 0.3740 = 0.8990"),
("blank",),
("sub", "Split on department"),
("table", ["value", "count", "senior", "junior", "Info"],
 [["sales", "110", "30", "80", "0.8454"],
  ["systems", "31", "8", "23", "0.8238"],
  ["marketing", "14", "10", "4", "0.8631"],
  ["secretary", "10", "4", "6", "0.9710"]], "lrrrr", {}),
("math", "Info_dept(D) = (110/165)(0.8454)"),
("math", "   + (31/165)(0.8238) + (14/165)(0.8631)"),
("math", "   + (10/165)(0.9710) = 0.8504"),
("math", "Gain(department) = 0.8990 - 0.8504 = 0.0486"),
("blank",),
("sub", "Split on age"),
("table", ["value", "count", "senior", "junior", "Info"],
 [["21...25", "20", "0", "20", "0"],
  ["26...30", "49", "0", "49", "0"],
  ["31...35", "79", "35", "44", "0.9906"],
  ["36...40", "10", "10", "0", "0"],
  ["41...45", "3", "3", "0", "0"],
  ["46...50", "4", "4", "0", "0"]], "lrrrr", {}),
("math", "Info_age(D) = (79/165)(0.9906) = 0.4743"),
("math", "Gain(age) = 0.8990 - 0.4743 = 0.4247"),
("blank",),
("sub", "Split on salary"),
("table", ["value", "count", "senior", "junior", "Info"],
 [["26K...30K", "46", "0", "46", "0"],
  ["31K...35K", "40", "0", "40", "0"],
  ["36K...40K", "4", "4", "0", "0"],
  ["41K...45K", "4", "0", "4", "0"],
  ["46K...50K", "63", "40", "23", "0.9468"],
  ["66K...70K", "8", "8", "0", "0"]], "lrrrr", {}),
("math", "Info_salary(D) = (63/165)(0.9468) = 0.3615"),
("math", "Gain(salary) = 0.8990 - 0.3615 = 0.5375"),
("blank",),
("sub", "Choosing the root"),
("table", ["attribute", "Gain"],
 [["salary", "0.5375"],
  ["age", "0.4247"],
  ["department", "0.0486"]], "lr", {0: "key"}),
("p", "Salary has the highest gain, so salary is the root. Five of its six "
      "branches are pure and become leaves. Only 46K...50K is mixed, with "
      "40 senior and 23 junior."),
("blank",),
("sub", "Splitting the 46K...50K branch (63 tuples)"),
("math", "Info(D') = -(40/63)log2(40/63)"),
("math", "          -(23/63)log2(23/63) = 0.9468"),
("p", "Department splits it into sales 30 senior, systems 23 junior and "
      "marketing 10 senior. Every part is pure, so Gain = 0.9468. Age also "
      "gives pure parts, but in four branches instead of three."),
("p", "Both reach the full gain, so choose department: it has the smaller "
      "SplitInfo and therefore the higher gain ratio."),
("p", "The final decision tree:"),
("svg", "decision_tree"),
("blank",),
("part", "(c) Given a data tuple having the values \"systems,\" \"26...30,\" "
         "and \"46-50K\" for the attributes department, age, and salary, "
         "respectively, what would a naive Bayesian classification of the "
         "status for the tuple be?"),
("ans", "X = (systems, 26...30, 46K...50K). Find P(X|Ci)P(Ci) for each "
        "class and pick the larger. The priors:"),
("math", "P(senior) =  52/165 = 0.3152"),
("math", "P(junior) = 113/165 = 0.6848"),
("sub", "Class senior (52 tuples)"),
("math", "P(systems | senior)   =  8/52 = 0.1538"),
("math", "P(26...30 | senior)   =  0/52 = 0"),
("math", "P(46K...50K | senior) = 40/52 = 0.7692"),
("math", "P(X | senior) = 0.1538 x 0 x 0.7692 = 0"),
("sub", "Class junior (113 tuples)"),
("math", "P(systems | junior)   = 23/113 = 0.2035"),
("math", "P(26...30 | junior)   = 49/113 = 0.4336"),
("math", "P(46K...50K | junior) = 23/113 = 0.2035"),
("math", "P(X | junior) = 0.2035 x 0.4336 x 0.2035"),
("math", "             = 0.01796"),
("sub", "Compare"),
("math", "P(X|senior)P(senior) = 0 x 0.3152 = 0"),
("math", "P(X|junior)P(junior) = 0.01796 x 0.6848"),
("math", "                     = 0.01230"),
("p", "0.01230 > 0, so the naive Bayesian classifier predicts "
      "status = junior."),
("p", "No senior tuple is aged 26...30, so one zero wipes out the senior "
      "product. With the Laplacian correction, add 1 to each count; the "
      "senior score becomes 0.00062 and junior still wins at 0.01190."),

# =========================================================== 6.17
("q", "Problem 6.17"),
("stmt", "The data tuples of Fig. 6.28 are sorted by decreasing probability "
         "value, as returned by a classifier. For each tuple, compute the "
         "values for the number of true positives (TP), false positives "
         "(FP), true negatives (TN), and false negatives (FN). Compute the "
         "true positive rate (TPR) and false positive rate (FPR). Plot the "
         "ROC curve for the data."),
("ans", "There are 5 positive (P) and 5 negative (N) tuples. Move the "
        "threshold down one tuple at a time. Every tuple at or above it is "
        "predicted positive."),
("math", "TPR = TP / (TP + FN) = TP / 5"),
("math", "FPR = FP / (FP + TN) = FP / 5"),
("table", ["#", "class", "prob", "TP", "FP", "TN", "FN", "TPR", "FPR"],
 [["1", "P", "0.95", "1", "0", "5", "4", "0.2", "0.0"],
  ["2", "N", "0.85", "1", "1", "4", "4", "0.2", "0.2"],
  ["3", "P", "0.78", "2", "1", "4", "3", "0.4", "0.2"],
  ["4", "P", "0.66", "3", "1", "4", "2", "0.6", "0.2"],
  ["5", "N", "0.60", "3", "2", "3", "2", "0.6", "0.4"],
  ["6", "P", "0.55", "4", "2", "3", "1", "0.8", "0.4"],
  ["7", "N", "0.53", "4", "3", "2", "1", "0.8", "0.6"],
  ["8", "N", "0.52", "4", "4", "1", "1", "0.8", "0.8"],
  ["9", "N", "0.51", "4", "5", "0", "1", "0.8", "1.0"],
  ["10", "P", "0.40", "5", "5", "0", "0", "1.0", "1.0"]], "llrrrrrrr",
 {0: "ok", 2: "ok", 3: "ok", 5: "ok", 9: "ok"}),
("p", "A P tuple moves the curve up by 0.2. An N tuple moves it right by "
      "0.2. Plot (FPR, TPR) for each row, starting from (0, 0):"),
("svg", "roc_curve"),
("p", "The area under the curve, as rectangles of width 0.2:"),
("math", "AUC = 0.2(0.2) + 0.2(0.6) + 0.2(0.8)"),
("math", "    + 0.2(0.8) + 0.2(0.8) = 0.64"),
("p", "0.64 is above 0.5, the diagonal of random guessing, so the "
      "classifier is better than chance but far from perfect."),

# =========================================================== 8.2
("q", "Problem 8.2"),
("stmt", "Suppose that the data mining task is to cluster points (with "
         "(x, y) representing location) into three clusters, where the "
         "points are A1(2, 10), A2(2, 5), A3(8, 4), B1(5, 8), B2(7, 5), "
         "B3(6, 4), C1(1, 2), C2(4, 9). The distance function is Euclidean "
         "distance. Suppose initially we assign A1, B1, and C1 as the center "
         "of each cluster, respectively. Use the k-means algorithm to show "
         "only"),
("part", "(a) The three cluster centers after the first round of execution."),
("ans", "Round 1. Distance from each point to the initial centres "
        "m1 = A1(2,10), m2 = B1(5,8) and m3 = C1(1,2):"),
("math", "d(p, m) = sqrt((x1 - x2)^2 + (y1 - y2)^2)"),
("table", ["point", "to m1", "to m2", "to m3", "cluster"],
 [["A1 (2,10)", "0.00", "3.61", "8.06", "1"],
  ["A2 (2,5)", "5.00", "4.24", "3.16", "3"],
  ["A3 (8,4)", "8.49", "5.00", "7.28", "2"],
  ["B1 (5,8)", "3.61", "0.00", "7.21", "2"],
  ["B2 (7,5)", "7.07", "3.61", "6.71", "2"],
  ["B3 (6,4)", "7.21", "4.12", "5.39", "2"],
  ["C1 (1,2)", "8.06", "7.21", "0.00", "3"],
  ["C2 (4,9)", "2.24", "1.41", "7.62", "2"]], "lrrrr", {}),
("p", "Example: A2 to m3 = sqrt(1^2 + 3^2) = sqrt(10) = 3.16, which is the "
      "smallest of the three, so A2 joins cluster 3."),
("p", "Clusters after round 1: C1 = {A1}, C2 = {A3, B1, B2, B3, C2}, "
      "C3 = {A2, C1}. The new centres are the means:"),
("math", "m1 = (2, 10)"),
("math", "m2 = ((8+5+7+6+4)/5, (4+8+5+4+9)/5) = (6, 6)"),
("math", "m3 = ((2+1)/2, (5+2)/2) = (1.5, 3.5)"),
("p", "The three cluster centres after the first round are (2, 10), "
      "(6, 6) and (1.5, 3.5)."),
("blank",),
("part", "(b) The final three clusters."),
("ans", "Repeat until no point changes cluster."),
("sub", "Round 2, centres (2,10), (6,6), (1.5,3.5)"),
("table", ["point", "to m1", "to m2", "to m3", "cluster"],
 [["A1", "0.00", "5.66", "6.52", "1"],
  ["A2", "5.00", "4.12", "1.58", "3"],
  ["A3", "8.49", "2.83", "6.52", "2"],
  ["B1", "3.61", "2.24", "5.70", "2"],
  ["B2", "7.07", "1.41", "5.70", "2"],
  ["B3", "7.21", "2.00", "4.53", "2"],
  ["C1", "8.06", "6.40", "1.58", "3"],
  ["C2", "2.24", "3.61", "6.04", "1"]], "lrrrr", {7: "key"}),
("p", "C2 moves to cluster 1. New centres:"),
("math", "m1 = ((2+4)/2, (10+9)/2) = (3, 9.5)"),
("math", "m2 = ((8+5+7+6)/4, (4+8+5+4)/4)"),
("math", "   = (6.5, 5.25)"),
("math", "m3 = (1.5, 3.5)"),
("sub", "Round 3, centres (3,9.5), (6.5,5.25), (1.5,3.5)"),
("table", ["point", "to m1", "to m2", "to m3", "cluster"],
 [["A1", "1.12", "6.54", "6.52", "1"],
  ["A2", "4.61", "4.51", "1.58", "3"],
  ["A3", "7.43", "1.95", "6.52", "2"],
  ["B1", "2.50", "3.13", "5.70", "1"],
  ["B2", "6.02", "0.56", "5.70", "2"],
  ["B3", "6.26", "1.35", "4.53", "2"],
  ["C1", "7.76", "6.39", "1.58", "3"],
  ["C2", "1.12", "4.51", "6.04", "1"]], "lrrrr", {3: "key"}),
("p", "B1 moves to cluster 1. New centres:"),
("math", "m1 = ((2+5+4)/3, (10+8+9)/3) = (3.67, 9)"),
("math", "m2 = ((8+7+6)/3, (4+5+4)/3) = (7, 4.33)"),
("math", "m3 = (1.5, 3.5)"),
("sub", "Round 4, centres (3.67,9), (7,4.33), (1.5,3.5)"),
("table", ["point", "to m1", "to m2", "to m3", "cluster"],
 [["A1", "1.94", "7.56", "6.52", "1"],
  ["A2", "4.33", "5.04", "1.58", "3"],
  ["A3", "6.62", "1.05", "6.52", "2"],
  ["B1", "1.67", "4.18", "5.70", "1"],
  ["B2", "5.21", "0.67", "5.70", "2"],
  ["B3", "5.52", "1.05", "4.53", "2"],
  ["C1", "7.49", "6.44", "1.58", "3"],
  ["C2", "0.33", "5.55", "6.04", "1"]], "lrrrr", {}),
("p", "No point changes cluster in round 4, so the algorithm has "
      "converged. The final three clusters:"),
("table", ["cluster", "members", "centre"],
 [["1", "A1(2,10), B1(5,8), C2(4,9)", "(3.67, 9)"],
  ["2", "A3(8,4), B2(7,5), B3(6,4)", "(7, 4.33)"],
  ["3", "A2(2,5), C1(1,2)", "(1.5, 3.5)"]], "lll",
 {0: "key", 1: "key", 2: "key"}),
("svg", "kmeans_plot"),

# =========================================================== 8.17
("q", "Problem 8.17"),
("stmt", "Describe each of the following clustering algorithms in terms of "
         "the following criteria: (1) shapes of clusters that can be "
         "determined; (2) input parameters that must be specified; and (3) "
         "limitations."),
("part", "(a) k-means"),
("ans", "(1) Shapes: spherical, convex clusters of similar size."),
("p", "(2) Input: k, the number of clusters."),
("p", "(3) Limitations: k must be given in advance. The result depends on "
      "the initial centres and can be a local optimum. Outliers pull the "
      "mean away. It needs numeric data, because it computes a mean. It "
      "cannot find non-convex clusters."),
("blank",),
("part", "(b) k-medoids"),
("ans", "(1) Shapes: spherical, convex clusters, the same as k-means."),
("p", "(2) Input: k, the number of clusters."),
("p", "(3) Limitations: k must be given in advance. Each iteration of PAM "
      "costs O(k(n-k)^2), so it does not scale to large data. It still "
      "fails on non-convex shapes. It is more robust to outliers than "
      "k-means, because a medoid is a real object."),
("blank",),
("part", "(c) BIRCH"),
("ans", "(1) Shapes: spherical. A CF-tree summarises each subcluster by "
        "its radius or diameter, which suits round clusters."),
("p", "(2) Input: the branching factor B and the threshold T of the "
      "CF-tree, and k if a global clustering step follows."),
("p", "(3) Limitations: numeric data only. The result depends on the "
      "order the data arrives in and on the choice of T. It handles "
      "non-spherical clusters poorly."),
("blank",),
("part", "(d) DBSCAN"),
("ans", "(1) Shapes: arbitrary. Any density-connected region becomes a "
        "cluster, and sparse points are marked as noise."),
("p", "(2) Input: Eps, the neighbourhood radius, and MinPts, the least "
      "number of points that makes a core point. The number of clusters is not needed."),
("p", "(3) Limitations: one global Eps and MinPts cannot fit clusters of "
      "very different density. The result is sensitive to both values. "
      "Distances lose meaning in high dimensions. Without a spatial index "
      "it costs O(n^2)."),
]
