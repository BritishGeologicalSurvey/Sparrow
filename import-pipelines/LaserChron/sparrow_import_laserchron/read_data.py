def itercells(df):
    for i, r in df.iterrows():
        for j, c in r.iteritems():
            yield (i,j), c

def find_last_column(df):
    last_col = None
    # Find last column of data based on
    # where "Concordia" column is
    for ix, c in itercells(df):
        try:
            assert c.lower().startswith("conc")
            last_col = ix
            break
        except (AssertionError, AttributeError):
            pass

    # Double check with another method (look
    # for columns that are _almost_ empty)
    # number of defined values in each column
    n_vals = df.isnull().values.sum(axis=0)
    n_rows = df.shape[0]
    last_col = next(i
        for (i,n) in list(enumerate(n_vals))[::-1]
        if n < n_rows/2)

    # These two methods serve as a sanity check
    # that we are dealing with a "normal" ETAgeCalc
    # or NuAgeCalc file
    assert ix[1] == last_col
    return last_col

def extract_data(df):
    if df.iloc[0,0].startswith("Table"):
        df = df[1:]

    last_col_ix = find_last_column(df)

    # Knowing the last column of data, we serialize all later non-zero
    # values (assumed to be comments/annotations that might be worth carrying
    # along) into one comment field. These may not correspond directly to the
    # data row...
    comment_ix = last_col_ix+1
    data = df.iloc[:,:comment_ix+1]
    comments = df.iloc[:,comment_ix:]
    for i,row in comments.iterrows():
        v = list(row.dropna().values)
        if len(v) == 0: continue
        data.iloc[i,comment_ix] = ",".join(v)
