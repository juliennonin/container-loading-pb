# %%
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection


# %%
class RectangularCuboid():
    def __init__(self, pos, dim):
        self.pos = pos
        self.dim = dim
    
    @property
    def vertices(self):
        x, y, z = self.pos
        w, l, h = self.dim
        return np.array([[x, y, z], [x, y+l, z], [x+w, y+l, z],[x+w, y, z],
                [x, y, z+h], [x, y+l, z+h], [x+w, y+l, z+h], [x+w, y, z+h]])
    
    @property
    def faces(self):
        vertices = self.vertices
        return [[vertices[0], vertices[1], vertices[2], vertices[3]],
                [vertices[0], vertices[1], vertices[5], vertices[4]],
                [vertices[1], vertices[2], vertices[6], vertices[5]],
                [vertices[2], vertices[3], vertices[7], vertices[6]],
                [vertices[3], vertices[0], vertices[4], vertices[7]],
                [vertices[4], vertices[5], vertices[6], vertices[7]]]

    def draw(self, ax):
        faces = Poly3DCollection(self.faces, linestyle = '-', linewidths=1,
            edgecolors=(0,0,1))
        ax.add_collection3d(faces)
        # Plot the points themselves to force the scaling of the axes
        vertices = self.vertices
        # ax.scatter(vertices[:,0], vertices[:,1], vertices[:,2], s=0)


# %%
# get_ipython().run_line_magic('matplotlib', 'qt')
c = RectangularCuboid([0, 0, 0], [1, 4, 5])
fig = plt.figure(figsize=plt.figaspect(1)*1.5)
ax = fig.gca(projection='3d')
ax.scatter([0,5], [0,5], [0,5], s=0)
# scaling = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
# ax.auto_scale_xyz(*[[np.min(scaling), np.max(scaling)]]*3)
c.draw(ax)


# %%
class BoxType():
    def __init__(self, dim, permutation=[0,0,1]):
        assert len(permutation) == 3, "permutation must be a list of 3 items"
        assert permutation[2] == 1, "the vertical aligmement of the z-axis must be allowed"
        
        self.dim = np.array(dim)
        
        # Set all permutation allowed
        orientations = [(self.dim[[2,1,0]], self.dim[[1,2,0]]),
                        (self.dim[[0,2,1]], self.dim[[2,0,1]]),
                        (self.dim[[0,1,2]], self.dim[[1,0,2]])]
        self.permuted_boxes = []
        for i, vertical_alignment_allowed in enumerate(permutation):
            if vertical_alignment_allowed:
                self.permuted_boxes.extend(orientations[i])
        self.permuted_boxes = np.array(self.permuted_boxes)
            


# %%
class Box():
    def __init__(self, dim, orientation_allowed=[1,1,1]):
        self.dim = dim


# %%
class Container():
    def __init__(self, dim, boxes):
        self.dim = dim
        pass


# %%
class Cargo():
    pass

