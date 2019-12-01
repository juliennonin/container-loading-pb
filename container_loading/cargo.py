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
class Box():
    def __init__(self, dim, boxtype):
        self.dim = np.array(dim)
        self.type = boxtype

    @property
    def volume(self):
        return np.prod(self.dim)
    
    def __repr__(self):
        return f"{mess.YELLOW}{'·'.join([str(d) for d in self.dim])}{mess.END}"

    def draw(self, pos, ax):
        RectangularCuboid(pos, self.dim).draw(ax, self.type.color, self.type.color + (0.1,))

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
                self.permuted_boxes.append(Box(orientations[i][0], self))
                self.permuted_boxes.append(Box(orientations[i][1], self))         
    
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

    @property
    def volume(self):
        return self.Ntot * self.box.volume

    def __gt__(self, other):
        return self.volume > other.volume

    def __repr__ (self):
    		return mess.GREEN + 'x'.join(str(n) for n in self.N) + ' ' \
		+ mess.YELLOW + '·'.join([str(d) for d in self.dim]) \
		+ mess.BLUE + ' (' + str(self.pos)[1:-1].replace(', ', ' ') +')' + mess.END

    def draw(self, ax):
        for n in np.ndindex(*self.N):
            self.box.draw(n * self.box.dim + self.pos, ax)

#%%
class Space():
    def __init__(self, pos, dim):
        self.dim = np.array(dim)
        self.pos = np.array(pos)
    
    def find_max_blocks(self, cargo):
        blocks = []
        for boxtype, t in cargo.items():
            for box in boxtype.permuted_boxes:
                Nmax = 3*[0]
                if (t != 0) and np.all(self.dim >= box.dim):
                    Nmax[2] = min(int(self.dim[2] / box.dim[2]), t)
                    Nmax[1] = min(int(self.dim[1] / box.dim[1]), int(t / Nmax[2]))
                    Nmax[0] = min(int(self.dim[0] / box.dim[0]), int(t / (Nmax[2]*Nmax[1])))
                    blocks.append(Block(box, Nmax, self))
        return blocks
    
    def split(self, block):
        spaces = []
        sp0, sp1, sp2 = self.pos
        bd0, bd1, bd2 = block.dim
        sd0, sd1, sd2 = self.dim
        spaces.append(Space([sp0, sp1+bd1, sp2], [bd0, sd1-bd1, sd2])) # side space
        spaces.append(Space([sp0, sp1, sp2+bd2], [bd0, bd1, sd2-bd2])) # top space
        spaces.append(Space([sp0+bd0, sp1 , sp2], [sd0-bd0, sd1, sd2])) # front space
        return spaces
    
    def distance(self):
        return np.sqrt(np.sum(self.pos))

    def __repr__(self):
        return mess.YELLOW + '·'.join([str(d) for d in self.dim]) + mess.BLUE + ' (' + str(self.pos)[1:-1].replace(', ', ' ') +')' + mess.END

#%%
class Container():
    def __init__(self, dim, cargo):
        self.dim = np.array(dim)
        self.spaces = [Space([0,0,0], self.dim)]
        self.blocks = []
        self.cargo = cargo
    
    @property
    def volume(self):
        return np.prod(self.dim)

    def fill(self, eval=max):
        sorted(self.spaces, key=Space.distance)
        space = self.spaces.pop(0)
        blocks_possible = space.find_max_blocks(self.cargo)
        if blocks_possible:
            new_block = eval(blocks_possible)
            new_spaces = space.split(new_block)
            self.spaces.extend(new_spaces)
            self.blocks.append(new_block)
            self.cargo[new_block.box.type] -= new_block.Ntot
        
    def draw(self):
        fig = plt.figure(figsize=plt.figaspect(1)*1.5)
        ax = fig.gca(projection='3d')
        ax.scatter(*[[0, max(self.dim)]]*3, s=0)
        RectangularCuboid([0,0,0], self.dim).draw(ax, (0.7,0.7,0.7,1), (1,1,1,0))
        for block in self.blocks:
            block.draw(ax)


#%%
B1 = BoxType([20, 24, 18])
B2 = BoxType([48, 9, 40], [1,1,1])
container = Container([74, 50, 50], {B1:4, B2:3})

#%%
container.fill()
container.draw()


# %%
