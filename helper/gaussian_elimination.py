def reduced_row_echelon_form(matrix):
    numpivots = 0
    for j in range(matrix.shape[1]):  # For each column
        if numpivots >= matrix.shape[0]:
            break
        pivotrow = numpivots
        while pivotrow < matrix.shape[0] and matrix[pivotrow, j] == 0:
            pivotrow += 1
        if pivotrow == matrix.shape[0]:
            continue  # Cannot eliminate on this column
        matrix[[numpivots, pivotrow]] = matrix[[pivotrow, numpivots]]
        pivotrow = numpivots
        numpivots += 1

        # Eliminate rows below
        for i in range(pivotrow + 1, matrix.shape[0]):
            if matrix[i, j]:
                matrix[i, :][j:] = matrix[i, :][j:] ^ matrix[pivotrow, :][j:]
    for i in reversed(range(numpivots)):
        # Find pivot
        pivotcol = 0
        while pivotcol < matrix.shape[1] and matrix[i, pivotcol] == 0:
            pivotcol += 1
        if pivotcol == matrix.shape[1]:
            continue  # Skip this all-zero row

        # Eliminate rows above
        for j in range(i):
            if matrix[j, pivotcol]:
                matrix[j, :][pivotcol:] = matrix[j, :][pivotcol:] ^ matrix[i, :][pivotcol:]
    return matrix, numpivots

