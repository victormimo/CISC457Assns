import numpy as np

data = np.array([[[1,2,3],[2,2,3],[3,2,3],[1,2,3]],
                 [[4,2,3],[5,2,3],[6,2,3],[1,2,3]],
                 [[7,2,3],[8,2,3],[9,2,3],[1,2,3]],
                 [[4,2,3],[5,2,3],[6,2,3],[1,2,3]]
                 ])
data1 = np.array([[1,2,3,1],
                 [4,5,6,1],
                 [7,8,9,1],
                 [4,5,6,1]
                 ])

def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w, d = arr.shape
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))
print blockshaped(data,2,2)
