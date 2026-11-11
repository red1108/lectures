// Submitted manuscript, Algorithm 2: Boundary(T, m).
// The frontier is a drawing aid: replace a subtree root by its two children
// before descending. It is not a record of occupied quantum registers.
export interface BoundaryFrame {
  node: number
  target: number
  line: number
  label: string
  boundary: number[]
  expanded: number[]
  added: number[]
}

export function boundaryExpansion(height: number, size: number): BoundaryFrame[] {
  if (!Number.isInteger(height) || height < 1 || !Number.isInteger(size)
    || size < 1 || size > 2 ** (height - 1)) {
    throw new RangeError('Boundary size must lie between 1 and the number of leaves')
  }
  const boundary = [1]
  const expanded: number[] = []
  const frames: BoundaryFrame[] = []
  function record(node: number, target: number, line: number, label: string, added: number[] = []) {
    frames.push({node, target, line, label, added, boundary: [...boundary], expanded: [...expanded]})
  }
  record(1, size, 0, 'B = {1}')
  function visit(node: number, target: number): number[] {
    if (target === 1) {
      record(node, target, 2, `return {${node}}`)
      return [node]
    }
    const left = 2 * node, right = left + 1
    const leftSize = Math.ceil(target / 2), rightSize = Math.floor(target / 2)
    boundary.splice(boundary.indexOf(node), 1, left, right)
    expanded.push(node)
    record(left, leftSize, 3, `${node} → {${left}, ${right}}`, [left, right])
    const leftBoundary = visit(left, leftSize)
    record(right, rightSize, 4, `Boundary(T${right}, ${rightSize})`)
    const rightBoundary = visit(right, rightSize)
    record(node, target, 5, 'return B_L ∪ B_R')
    return [...leftBoundary, ...rightBoundary]
  }
  visit(1, size)
  return frames
}
