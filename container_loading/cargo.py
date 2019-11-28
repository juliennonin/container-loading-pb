# %%
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

#%%
COLORS = [(0,0,1), (1,0,0), (0,0.6,0.25)]

class mess:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#%%
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

    def draw(self, ax, color_vertices=(0,0,1), color_faces=(0.7,0.7,0.7)):
        faces = Poly3DCollection(self.faces, linestyle = '-', linewidths=1,
            edgecolors=color_vertices, facecolor=(color_faces))
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
class Box():
    def __init__(self, dim, color):
        self.dim = np.array(dim)
        self.color = color
    
    def __repr__(self):
        return f"{mess.YELLOW}{'·'.join([str(d) for d in self.dim])}{mess.END}"

    def draw(self, pos, ax):
        RectangularCuboid(pos, self.dim).draw(ax, self.color, self.color + (0.1,))

# %%
class BoxType():
    id = 0
    def __init__(self, size, permutation=[0,0,1]):
        assert len(permutation) == 3, "permutation must be a list of 3 items"
        assert permutation[2] == 1, "the vertical aligmement of the z-axis must be allowed"
        
        self.size = np.array(size)
        self.id = BoxType.id
        BoxType.id += 1
        self.color = COLORS[self.id % len(COLORS)]
        
        # Set all permutation allowed
        orientations = [(self.size[[2,1,0]], self.size[[1,2,0]]),
                        (self.size[[0,2,1]], self.size[[2,0,1]]),
                        (self.size[[0,1,2]], self.size[[1,0,2]])]
        self.permuted_boxes = []
        for i, vertical_alignment_allowed in enumerate(permutation):
            if vertical_alignment_allowed:
                self.permuted_boxes.append(Box(orientations[i][0], self.color))
                self.permuted_boxes.append(Box(orientations[i][1], self.color))         
    
    def __repr__(self):
        return f"({self.id}) {mess.YELLOW}{'·'.join([str(d) for d in self.size])}{mess.END}"

#%%
class Block():
    def __init__(self, box, N, space):
        self.box = box
        self.N = np.array(N)
        self.space = space
        self.pos = space.pos
    
    @property
    def dim(self):
        return self.N * self.box.dim

    @property
    def Ntot(self):
        return np.prod(self.N)

    def __repr__ (self):
    		return mess.GREEN + 'x'.join(str(n) for n in self.N) + ' ' \
		+ mess.YELLOW + '·'.join([str(d) for d in self.dim]) \
		+ mess.BLUE + ' (' + str(self.pos)[1:-1].replace(', ', ' ') +')' + mess.END

    def draw(self, ax):
        for i, j, k in np.ndindex(*self.N):
            self.box.draw([i*self.box.dim[0] , j*self.box.dim[1] , k*self.box.dim[2]], ax)


#%%
class Space():
    def __init__(self, pos, dim):
        self.dim = dim
        self.pos = pos
    
    def find_max_blocks(self, cargo):
        blocks = []
        for boxtype, t in cargo.items():
            for box in boxtype.permuted_boxes:
                Nmax = 3*[0]
                if (t != 0) and all([self.dim[i] >= box.dim[i] for i in range(3)]):
                    Nmax[2] = min(int(self.dim[2] / box.dim[2]), t)
                    Nmax[1] = min(int(self.dim[1] / box.dim[1]), int(t / Nmax[2]))
                    Nmax[0] = min(int(self.dim[0] / box.dim[0]), int(t / (Nmax[2]*Nmax[1])))
                    blocks.append(Block(box, Nmax, self))
        return blocks
#%%
B1 = BoxType([10, 7, 3])
B2 = BoxType([11, 4, 2.5], (1,1,1))
S = Space([0,0,0], [37, 25, 22])
cargo = {B1:4, B2:3}
# for boxtype, t in cargo.items():
#     print(t, boxtype, sep='\t')
blocks = S.find_max_blocks(cargo)
blocks

#%%
fig = plt.figure()
ax = fig.gca(projection='3d')
blocks[0].draw(ax)
ax.scatter(*[[0,max(blocks[0].dim)]]*3, s=0)
plt.show()


# %%
