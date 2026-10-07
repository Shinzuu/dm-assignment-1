"""Content for the DM Assignment-1 handwriting sheets.

Every entry is a block. build.py costs each block in ruled lines, paginates at
LINES_PER_SHEET, and refuses to build if a line of text is wider than the
writing area. Keep prose lines to roughly seven words.

Block forms:
    ("q",     "Question 3.4")            heading, 1 line, bold
    ("ln",    "text")                    one ruled line
    ("ind",   "text")                    indented one step
    ("ind2",  "text")                    indented two steps
    ("math",  "a(P1) = (2 + 4) / 2 = 3") monospace, 1 line
    ("quote", "text")                    serif, the textbook's wording
    ("blank",)                           one empty rule
    ("table", [headers], [[cells]], "llr")   1 header + n body rows
    ("draw",  "What to draw", ["line", ...])  a dashed instruction box
"""

TITLE = "Data Mining Assignment-1 — worked solutions"
COURSE = "CSE 4333 · Han, Pei & Tong 4th ed. · Chapters 3, 4, 6, 8"
BLURB = (
    "The exam is Wednesday 7 October. Part B is the revision half — start there. "
    "Part A holds the eight assignment solutions as F4 sheets to copy by hand "
    "for the 28 October submission: problem statement first, then the answer."
)
DATES = [
    ("Final exam", "Wed 7 October, 2:00–5:00 PM",
     "CSE 4333(V4), 3 hours — Chapters 3, 4, 6 and 8, one question from each"),
    ("Assignment-1 due", "28 October",
     "handwritten, to the Section Office, 1–2 days' grace"),
]

SHEETS_INTRO = (
    "Copy straight down, one ruled line at a time. Each sheet is one F4 page "
    "at 32 lines. Blue is the problem statement from the book, black is the "
    "answer. Table rows: green kept or frequent, red pruned, yellow the result."
)

# --------------------------------------------------------------------------
# Chapter 3 — Data warehousing and OLAP
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Videos. Every id below was checked against YouTube's oEmbed endpoint and
# returned 200 with the title and channel recorded here. One search result
# that looked plausible, slQ4Xd_c7lY, was a 404 and is not listed.
# --------------------------------------------------------------------------

VIDEOS_INTRO = (
    "One video per technique, nothing more. If you only have an hour, watch "
    "the three marked start here — they are what he named in class. Each "
    "opens in a new tab."
)

VIDEOS = [
 ("Clustering evaluation", [
   ("wW1tgWtkj4I", "Elbow method and silhouette coefficient",
    "Mahesh Huddar", "Both the topics he named for the exam, worked numerically.", True),
   ("d1qAwe8hthM", "Hierarchical clustering, complete linkage",
    "Mahesh Huddar", "Complete linkage, which is the one on your syllabus. Single linkage is not.", True),
   ("FllcPjvztTI", "k-means, solved numerical example",
    "Mahesh Huddar", "The same shape as problem 8.2.", False),
 ]),
 ("Chapter 3 — warehousing and OLAP", [
   ("BLqE2EKiAy4", "OLAP operations with a real example",
    "Gate Smashers", "Roll-up, drill-down, slice, dice and pivot. Start here if 3.4(c) made no sense.", True),
   ("ZMPHwpw4Dn4", "Star, snowflake and fact constellation schemas",
    "AmpCode", "Exactly the three classes problem 3.4(a) asks you to enumerate.", False),
 ]),
 ("Chapter 4 — pattern mining", [
   ("C57cQKFJhz8", "Apriori, solved example",
    "Mahesh Huddar", "Candidate generation and pruning, step by step.", False),
   ("7oGz4PCp9jI", "FP-growth, solved example",
    "Mahesh Huddar", "Building the FP-tree and mining the conditional pattern bases.", False),
 ]),
 ("Chapter 6 — classification", [
   ("y6VwIcZAUkI", "Entropy and information gain in a decision tree",
    "Mahesh Huddar", "The calculation behind problem 6.7(b).", False),
   ("XzSlEA4ck2I", "Naive Bayes, solved example",
    "Mahesh Huddar", "The PlayTennis example; 6.7(c) is the same method.", False),
   ("w3nPQURW5bU", "ROC curve and AUC explained",
    "PM Expert", "What problem 6.17 is actually plotting.", False),
 ]),
]
