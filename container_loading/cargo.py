# %%
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import container_loading.tikz_to_png as tikz_to_png
#%%
COLORS = [(0,0,1), (1,0,0), (0,0.6,0.25)]
MAX_TIKZ_COLORS = 5

class mess:   
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'  # regular, 93m for high intensity
    BLUE = '\033[94m'
    PURPLE = '\033[95m'

#%%
class RectangularCuboid():
    """Geometrical rectangular cuboid in Euclidian space (x, y, z)
    Its origin is the bottom left corner of the back face.
    This class is mainly used to display any parallelepipedic shaped object.

    Attributes:
        pos {array of 3 floats} -- coordinates of its origin.
        dim {array of 3 floats} -- dimension resp. along the x, y and z-axis
            (length, width and heigth)
    """    

    def __init__(self, pos, dim):      
        self.pos = pos
        self.dim = dim

    @property
    def vertices(self):
        """Generate the coordinates of the 8 vertices of the cuboid.
        
        Returns:
            {list of 8 coord.} -- list of vertices
        """        
        x, y, z = self.pos
        w, l, h = self.dim
        return np.array([[x, y, z], [x, y+l, z], [x+w, y+l, z],[x+w, y, z],
                [x, y, z+h], [x, y+l, z+h], [x+w, y+l, z+h], [x+w, y, z+h]])
    
    @property
    def faces(self):
        """Generate the 6 faces of the cuboid.
        Each face is defined by a list of its 4 vertices.
        
        Returns:
            {list of 6 faces} -- list of faces
        """        
        vertices = self.vertices
        return [[vertices[0], vertices[1], vertices[2], vertices[3]],
                [vertices[0], vertices[1], vertices[5], vertices[4]],
                [vertices[1], vertices[2], vertices[6], vertices[5]],
                [vertices[2], vertices[3], vertices[7], vertices[6]],
                [vertices[3], vertices[0], vertices[4], vertices[7]],
                [vertices[4], vertices[5], vertices[6], vertices[7]]]

    def draw(self, ax, color_vertices=(0,0,1), color_faces=(0.7,0.7,0.7)):
        """Draw the rectangular cuboid in a given matplotlib.pyplot.axes.
        
        Arguments:
            ax {plt.axes} -- Axes in which the cuboid will be drawn
            color_vertices {tuple} -- RGB color of the vertices (default: {(0,0,1)})
            color_faces {tuple} -- RGB color of the faces (default: {(0.7,0.7,0.7)})
        """        
        faces = Poly3DCollection(self.faces, linestyle = '-', linewidths=1,
            edgecolors=color_vertices, facecolor=(color_faces))
        ax.add_collection3d(faces)
        # Plot the points themselves to force the scaling of the axes
        # vertices = self.verticesx
        # ax.scatter(vertices[:,0], vertices[:,1], vertices[:,2], s=0)

    def tikz(self, color):
        return r"\cuboid[l={0}, w={1}, h={2}, c={3}]{{({5}, {6}, {4})}}".format(*self.dim, color, *self.pos)

# %%
class Box():
    """Physical box that will be loaded into a container. Represent a feasible
    orientation of a given BoxType.
    
    Attributes:
        dim {list of 3 floats} -- dimension along the x, y and z-axis
        type {BoxType} -- type of the box
    """    
    def __init__(self, dim, boxtype):
        """[TODO] Check that dim is allowed by the boxtype"""
        self.dim = np.array(dim)
        self.type = boxtype

    @property
    def volume(self):        
        return np.prod(self.dim)
    
    def __repr__(self):
        return f"{mess.YELLOW}{'·'.join([str(d) for d in self.dim])}{mess.END}"

    def draw(self, pos, ax):
        RectangularCuboid(pos, self.dim).draw(ax, self.type.color, self.type.color + (0.1,))

    def tikz(self, pos):
        return RectangularCuboid(pos, self.dim).tikz('color' + str(self.type.id % MAX_TIKZ_COLORS))
# %%
class BoxType():
    """Boxes that share the same dimensions and possible orientations are
    grouped into BoxTypes.

    Arguments:
        size {list of 3 floats} -- cf. Attributes
        permutation {list of 3 booleans} -- represents the allowed orientation
            if permutation[i], then the vertical alignement (z-axis) of the
            i-th dimension is allowed ;
            otherwise, the i-th dimension cannot be aligned with the z-axis

    Attributes:
        size {list of 3 floats} -- dimension of the Boxes, regardless of the orientation
        id {int} -- index for identifying types
        color {tuple} -- RGB color used to draw a Box
        permuted_boxes {list of Boxes} -- All possible orientation of a BoxType
    """    
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
    """A Block is a composition of Boxes of the same BoxType.
    
    Attributes:
        box {Box} -- Box of which the Block is composed
        N {triplet of ints} -- N[0] is the number of boxes along the x-axis,
            so that N[0]*N[1]*N[2] is the total number of boxes in the block
        pos {coord.} -- position of the Block (i.e. of its bottom back left corner)
    """    
    def __init__(self, box, N, space):
        self.box = box
        self.N = np.array(N)
        # self.space = space
        self.pos = space.pos
    
    @property
    def dim(self):
        """Dimensions of the Block"""        
        return self.N * self.box.dim

    @property
    def Ntot(self):
        """Number of Boxes inside the Block"""
        return np.prod(self.N)

    @property
    def volume(self):
        """Volume of the Block"""
        return self.Ntot * self.box.volume

    def __gt__(self, other):
        return self.volume > other.volume

    def __repr__ (self):
    		return mess.GREEN + 'x'.join(str(n) for n in self.N) + ' ' \
		+ mess.YELLOW + '·'.join([str(d) for d in self.box.dim]) \
		+ mess.BLUE + ' (' + str(self.pos)[1:-1].replace(', ', ' ') +')' + mess.END

    def draw(self, ax):
        for n in np.ndindex(*self.N):
            self.box.draw(n * self.box.dim + self.pos, ax)

    def tikz(self, begin='', end='\n'):
        s = ""
        for n in np.ndindex(*self.N):
            s += begin
            s += self.box.tikz(n * self.box.dim + self.pos)
            s += end
        return s

#%%
class Space():
    """Empty cuboidal space, which we are trying to fill with Blocks (of Boxes).
    
    Attributes:
        pos {array of 3 floats} -- coordinates of its origin.
        dim {array of 3 floats} -- dimension resp. along the x, y and z-axis
    """
    def __init__(self, pos, dim):
        self.dim = np.array(dim)
        self.pos = np.array(pos)
    
    def find_max_blocks(self, cargo):
        """Given a set of BoxTypes (cargo), find all maximal Blocks that can
        fill the Space. (i.e. for each BoxType b in quantity q, find the biggest
        Block that can fit into the Space)
        
        Arguments:
            cargo {dict[BoxType,int]} -- available BoxTypes (key) and their quantity (value)
        
        Returns:
            blocks {list[Blocks]} -- maximal Blocks that can fit into the Space
        """        
        blocks = []
        for boxtype, q in cargo.items():
            for box in boxtype.permuted_boxes:
                Nmax = 3*[0]
                if (q != 0) and np.all(self.dim >= box.dim):
                    Nmax[2] = min(int(self.dim[2] / box.dim[2]), q)
                    Nmax[1] = min(int(self.dim[1] / box.dim[1]), int(q / Nmax[2]))
                    Nmax[0] = min(int(self.dim[0] / box.dim[0]), int(q / (Nmax[2]*Nmax[1])))
                    blocks.append(Block(box, Nmax, self))
        return blocks
    
    def split(self, block):
        """Return the 3 new spaces generated after the loading of a block into
        the Space
        
        Arguments:
            block {Block} -- Block that will be loaded into the Space
        
        Returns:
            spaces {list of 3 Spaces} -- [side space, top space, front space]
        
        [TODO]: Check that block is compatible with the space
        Idea: assert block.space == self
        """        
        spaces = []
        sp0, sp1, sp2 = self.pos
        bd0, bd1, bd2 = block.dim
        sd0, sd1, sd2 = self.dim
        spaces.append(Space([sp0, sp1+bd1, sp2], [bd0, sd1-bd1, sd2])) # side space
        spaces.append(Space([sp0, sp1, sp2+bd2], [bd0, bd1, sd2-bd2])) # top space
        spaces.append(Space([sp0+bd0, sp1 , sp2], [sd0-bd0, sd1, sd2])) # front space
        return spaces
    
    def distance(self):
        """Distance to the origin"""        
        return np.sqrt(np.sum(self.pos))

    def __eq__(self, other):
        return all(self.dim == other.dim) and all(self.pos == other.pos)

    def __repr__(self):
        return mess.YELLOW + '·'.join([str(d) for d in self.dim]) + mess.BLUE + ' (' + str(self.pos)[1:-1].replace(', ', ' ') +')' + mess.END

    def draw(self, ax):
        ax.scatter(*[[x, max(self.dim)] for x in self.pos], s=0)
        RectangularCuboid(self.pos, self.dim).draw(ax, (0.7,0.7,0.7,1), (1,1,1,0))
#%%
class Container():
    """Container in which boxes must be loaded.
    Container is described as a set of Spaces and Blocks.
    
    Attributes:
        dim {list of 3 floats} -- dimension resp. along x, y and z-axis
        cargo {dict[BoxType,int]} -- Boxtypes (and their quantity) that still
        blocks {list of Blocks} -- Blocks of boxes that have been loaded
        spaces {list of Space} -- the remaining spaces that can be filled
            need to be loaded in the container
    """    
    def __init__(self, dim, cargo):
        self.dim = np.array(dim)
        self.spaces = [Space([0,0,0], self.dim)]
        self.blocks = []
        self.cargo = cargo
    
    @property
    def volume(self):
        return np.prod(self.dim)

    def fill(self, eval=max):
        """[naiv] Select and fill one Block inside the Container
        
        Keyword Arguments:
            eval {function} -- Function to select one Block among a set
                of Blocks (default: {max})
        """        
        sorted(self.spaces, key=Space.distance)
        space = self.spaces.pop(0)
        blocks_possible = space.find_max_blocks(self.cargo)
        if blocks_possible:
            new_block = eval(blocks_possible)
            new_spaces = space.split(new_block)
            self.spaces.extend(new_spaces)
            self.blocks.append(new_block)
            self.cargo[new_block.box.type] -= new_block.Ntot
    
    def __repr__(self):
        s = str(self.cargo)
        for b in self.blocks:
            s += "({b.box.type.id})" + mess.GREEN + 'x'.join(str(n) for n in b.N) + mess.END +', '
        for f in self.spaces:
            s += mess.YELLOW + '·'.join([str(d) for d in f.dim]) + mess.END + ', '
        return s
        
    def draw(self):
        fig = plt.figure(figsize=plt.figaspect(1)*1.5)
        ax = fig.gca(projection='3d')
        ax.scatter(*[[0, max(self.dim)]]*3, s=0)
        RectangularCuboid([0,0,0], self.dim).draw(ax, (0.7,0.7,0.7,1), (1,1,1,0))
        for block in self.blocks:
            block.draw(ax)

    def tikz(self):
        s = r"\begin{tikzpicture}[scale=0.1, z={(200:1)}, x={(-30:.87)}]" + '\n'
        s += r"\containerBack{{{}}}{{{}}}{{{}}}".format(*self.dim)
        for b in self.blocks:
            s += '\n'
            s += b.tikz(begin='\t')
        s += r"\containerFront{{{}}}{{{}}}{{{}}}".format(*self.dim) + '\n'
        s += r"\end{tikzpicture}"
        return s

    def save_png(self, filename, dir='img'):
        with open(dir + '/' + filename + '.tex', 'w+') as f:
            f.write(r"\documentclass{standalone}" + '\n')
            f.write(fr"\input{{img/_cuboid.tex}}" + '\n')
            f.write(r"\begin{document}" + '\n')
            f.write(self.tikz())
            f.write('\n' + r"\end{document}")
        tikz_to_png.convert(dir, filename)
        return

#%%
if __name__ == "__main__":
    import os
    B1 = BoxType([20, 24, 18])
    B2 = BoxType([48, 9, 40], [1,1,1])
    container = Container([74, 50, 50], {B1:4, B2:3})
    container.fill()
    container.draw()
    container.fill()
    container.fill()
    container.save_png("test3")


# %%
