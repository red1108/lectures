template<class Computer>
void sequential_pebble(Computer& qc, int x) {
    if(!qc.leaf(x)) {
        auto [left, right] = qc.children(x);
        sequential_pebble(qc, left);
        sequential_pebble(qc, right);
    }
    qc.pebble(x);
    if(!qc.leaf(x)) {
        auto [left, right] = qc.children(x);
        release(qc, left);
        release(qc, right);
    }
}
