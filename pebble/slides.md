---
theme: '@slidev/theme-bricks'
title: 'Pebbling computations'
info: 'A visual introduction to reversible and spooky pebbling on binary trees.'
colorSchema: light
transition: fade
mdc: true
fonts:
  sans: 'Noto Sans'
  serif: 'DM Serif Display'
  mono: 'Fira Code'
---

# Pebbling computations

### Scheduling memory, one computation at a time

<div class="cover-byline">Mingyu Lee · Sanghyun Lee · Kabgyun Jeong</div>
<div class="cover-small">Reversible pebbling · Spooky pebbling · KSS · KMRV · Block cleanup</div>

<!--
이번 발표는 처음 접하는 청중을 대상으로 한다. pebble game의 규칙을 설명한 뒤 KSS, block cleanup, KMRV를 실제 스케줄로 살펴본다. 15–20분을 기준으로 각 trace의 핵심 순간만 보여준다.
-->

---
layout: default
---

# Pebble game

<PebbleRule />

<!--
네 정점의 line에서 직접 원을 클릭한다. 모든 원이 비어 있는 상태로 시작한다. 맨 왼쪽 start는 자유롭게 토글할 수 있고 나머지 정점은 바로 앞 정점이 pebbled일 때만 토글할 수 있다. Pebble은 저장된 값을 뜻한다. 성공한 toggle은 compute 또는 uncompute 한 번이므로 work가 1 증가한다. Peak는 Reset 이후 동시에 존재한 pebble 수의 최댓값이다. 목표는 final에만 돌을 남기는 것이다. Reset은 모든 돌을 비우고 work와 peak를 0으로 만든다.
-->

---
layout: default
---

# Pebbling a line

<div class="visual-intro">
<div class="intro-line">Compute → keep the output → uncompute</div>
<TracePlayer example="line-simple" intro intro-metrics />
</div>

<!--
약 90초. 가장 먼저 그래프가 계산의 의존성을 나타내는 모델임을 설명한다. 노드는 계산값이고 pebble은 그 값이 메모리에 존재한다는 뜻이다. 0번은 입력 의존성이 없는 첫 계산값이며 자유롭게 load하거나 uncompute할 수 있다. i→i+1 화살표는 이전 값이 다음 값의 입력이라는 뜻이다. 처음 3개 행동으로 계산을 설명하고, 끝까지 이동해 마지막 값만 보존하고 앞부분은 역순으로 정리하는 목표를 보여준다. 이 단순한 전략은 8개 값을 동시에 보관한다. Source: Craig Gidney, https://algassert.com/post/1905.
-->

---
layout: default
---

# Reversible pebbling on a line

<div class="visual-intro">
<div class="intro-line">Save a checkpoint. Recompute when needed.</div>
<TracePlayer example="line-reversible" intro />
<div class="intro-caption">8 → 4 registers <span>15 → 27 actions</span></div>
</div>

<!--
약 90초. 원문의 normal divide-and-conquer GIF와 동일한 재귀 구조를 8개 노드로 줄여 단계별로 재생한다. 각 노드의 predecessor가 있을 때만 pebble과 unpebble이 가능하다. 중간 checkpoint를 보존하고 뒷부분을 계산한 뒤, 앞부분을 다시 계산해 checkpoint를 제거한다. 이 예시의 값은 정확한 실행 결과이며 일반적인 최적성 주장은 아니다. 핵심은 메모리를 줄이면 재계산이 증가할 수 있다는 점이다. Source: https://algassert.com/post/1905.
-->

---
layout: default
clicks: 2
---

# Measurement creates a ghost

<div class="measurement-math">
<div class="math-context">

$f(x),m\in\{0,1\}^k\qquad m\cdot f(x)=\sum_{j=1}^k m_j f_j(x)\pmod{2}$

</div>

$$
\sum_x \alpha_x |x\rangle |f(x)\rangle
$$

<div v-click="1">
<div class="measure-arrow">↓ <span>X-basis measurement · outcome m ∈ {0, 1}<sup>k</sup></span></div>

$$
\sum_x \alpha_x \textcolor{#a45f3e}{(-1)^{m\cdot f(x)}} |x\rangle
$$

</div>
<div v-click="2" class="ghost-summary">
<span class="small-stone stored"></span><span class="small-arrow">→</span><span class="small-stone deferred">G</span>
<span>Register freed · keep m · correct the phase later</span>
</div>
</div>

<!--
약 1분. f(x)는 k비트 값이고 m은 각 비트의 X 기저 측정 결과를 모은 k비트 문자열이다. 내적은 mod 2로 계산한다. 정규화된 입력 Σα_x|x>|f(x)>에서 <m_X|f(x)>=2^{-k/2}(-1)^{m·f(x)}이므로 비정규화된 남은 상태는 2^{-k/2}Σα_x(-1)^{m·f(x)}|x>다. 서로 다른 x가 직교하므로 각 결과 m의 확률은 2^{-k}다. 화면은 해당 결과에 조건부인 정규화 상태를 보여준다. x는 중첩 상태이므로 이 부호는 상대위상이 될 수 있다. 측정된 k개 큐비트는 버리거나 결과에 따라 초기화해 재사용할 수 있고 m은 고전적으로 저장한다. m이 영벡터이면 위상은 1이다. 논문의 결정적 모델은 측정 결과를 ghost로 기록하며 유리한 무작위 결과에 따른 절약은 이용하지 않는다. Ghost는 quantum value register가 아니라 보류한 위상 보정을 뜻한다.
Source: current manuscript, Section 2; Craig Gidney, Spooky Pebble Games and Irreversible Uncomputation (2019), https://algassert.com/post/1905.
-->

---
layout: default
clicks: 3
---

# Correcting the phase

<div class="correction-math">
<div class="correction-identity">

$Z(m)=\bigotimes_{j=1}^k Z^{m_j}\qquad Z(m)|y\rangle=(-1)^{m\cdot y}|y\rangle$

</div>
<div class="correction-row initial-state"><span>Fresh register</span>

$$
\sum_x\alpha_x(-1)^{m\cdot f(x)}|x\rangle|0^k\rangle
$$

</div>
<div v-click="1" class="correction-row"><span>Recompute</span>

$$
\xrightarrow{U_f}\sum_x\alpha_x(-1)^{m\cdot f(x)}|x\rangle|f(x)\rangle
$$

</div>
<div v-click="2" class="correction-row corrected"><span>Correct the phase</span>

$$
\xrightarrow{Z(m)}\sum_x\alpha_x|x\rangle|f(x)\rangle
$$

</div>
<div v-click="3" class="correction-row"><span>Uncompute</span>

$$
\xrightarrow{U_f^\dagger}\sum_x\alpha_x|x\rangle|0^k\rangle
$$

</div>
<div v-click="3" class="ghost-summary correction-summary">
<span class="small-stone deferred">G</span><span class="small-arrow">→</span><span class="small-stone stored"></span><span class="small-arrow">→</span><span class="small-stone empty"></span>
<span>Recompute + correct → uncompute</span>
</div>
</div>

<!--
약 90초. 직전 장에서 ghosting한 값의 입력 x가 다시 준비되어 있다고 가정한다. Fresh register는 재사용할 k큐비트 |0^k> 보조 레지스터다. U_f|x>|y>=|x>|y XOR f(x)> 로 정의한다. 첫 클릭에서 f(x)를 다시 계산한다. 두 번째 클릭에서는 결과 레지스터의 j번째 큐비트에 Z^{m_j}를 적용한다. Z(m)=⊗_j Z^{m_j}가 (-1)^{m·f(x)}를 한 번 더 곱하므로 기존 위상이 상쇄된다. 이 시점에서 ghost가 pebble로 바뀐다. 논문의 Peb는 이 재계산과 위상 보정을 함께 포함한다. 마지막 클릭에서 U_f^dagger로 보조 레지스터를 |0^k>으로 되돌리면 정점은 empty가 된다. 이는 별도의 Unp 동작이다. x가 여러 입력 레지스터를 뜻하면 재계산과 uncompute에는 이들이 모두 있어야 한다. Ghosting 자체는 이 입력들을 요구하지 않으므로 더 일찍 양자 메모리를 해제할 수 있다. Ghost의 측정 결과 m은 보정이 끝나면 버릴 수 있다.
Source: current manuscript, Section 2, ghosting and phase correction; https://algassert.com/post/1905.
-->

---
layout: default
---

# Measurement and correction circuit

<img class="measurement-circuit" src="/figures/measurement-correction.svg" alt="Register circuit showing X-basis measurement, classical outcome m, a released value register, and later recomputation, Z(m) correction, and uncomputation." />

<!--
회로는 레지스터 단위 그림이다. x는 입력 레지스터이며 f(x)는 k큐비트 값 레지스터다. 첫 두 선은 계산기저에서 얽힌 중첩 Σα_x|x>|f(x)>를 나타낸다. k큐비트 값에 H^{⊗k}를 적용하고 계산기저에서 측정하면 X 기저 측정과 같다. 출력 m은 k비트 고전 레지스터이므로 이중선으로 그린다. 측정 직후 해당 양자선은 끝나며 뒤의 빈 구간은 레지스터가 해제되어 있음을 나타낸다. 나중에 |0^k>를 준비하고 U_f로 값을 재계산한다. 이중선은 저장한 m을 Z(m)=⊗_j Z^{m_j}에 공급하는 고전적 feed-forward다. 이후 U_f^dagger를 적용하면 전체 상태는 Σα_x|x>|0^k>로 복구된다. 도중에 생긴 ghost는 보정 후 사라진다. x 선은 이 원리를 설명하기 위해 계속 유지한 예시다. 스케줄에서는 x를 다시 준비하는 추가 계산이 필요할 수 있다.
Source: current manuscript, Section 2. Circuit drawn for this presentation.
-->

---
layout: default
---

# Spooky pebbling on the same line

<div class="visual-intro">
<div class="intro-line">Leave ghosts. Return to correct them.</div>
<TracePlayer example="line-spooky" intro />
<div class="intro-caption">8 values · 3 registers</div>
</div>

<!--
약 2분. 원문의 constant-space GIF를 확인했다. 먼저 앞의 pebble을 만들고 뒤의 pebble을 ghost로 바꿔 두 pebble로 endpoint까지 진행한다. endpoint를 보존한 뒤 앞부분을 다시 sweep하고 가장 오른쪽 ghost부터 정리한다. 전체 trace를 모두 설명하지 말고, 15번째 행동 부근의 endpoint 보존 상태와 종료 상태를 slider로 보여준다. 원문의 GIF는 확률적으로 ghost가 남는 모델이며 ghost를 직접 제거하는 행동이 있다. 여기서는 현재 논문과 동일하게 매 ghosting에 보정 의무를 기록하고, ghost를 재계산하는 Peb와 별도의 Unp로 정리하도록 변환했다. 따라서 원문 GIF의 시간 숫자와 이 trace의 action 수를 동일시하지 않는다. Source: https://algassert.com/post/1905.
-->

---
layout: default
---

# Binary-tree dependencies

<div class="visual-intro">
<div class="intro-line">Both children present → toggle the parent</div>
<TracePlayer example="reversible" intro />
</div>

<!--
약 1분. 앞서 line에서는 입력이 하나였다. 이제 둘을 결합하는 연산의 의존성을 binary tree로 표현한다. 아래쪽 자식 정점들이 부모의 입력이며 화살표는 자식에서 부모 방향이다. 첫 3개 행동만 보여주어 4와 5를 준비해야 2를 계산할 수 있음을 설명하고 KSS로 넘어간다. 방향키로 다음 슬라이드로 이동하고 trace는 내부 버튼으로 조작한다.
-->

---
layout: default
---

# KSS: compute the root

<TracePlayer example="kss-root">
<template #code="{ step }">
<StepCode :clicks="step" />
</template>
</TracePlayer>

<!--
KSS는 Kornerup, Sadun, Soloveichik의 알고리즘이다. SequentialPebble 함수의 실행에서 실제 C++ scheduler가 기록한 동작을 재생한다. 강조 표시는 관찰된 pebble 또는 release 행동을 가리키는 것이며 호출 스택 전체를 표현하지는 않는다. 13개 action의 마지막에는 root가 남고 자식 정점에 ghost가 있다. Source: core/sequential_schedule.hpp; https://doi.org/10.22331/q-2025-02-18-1636.
-->

---
layout: default
---

# KSS in action

<div class="split-demo"><div>
<div class="lead small">Keep the root.<br>Clear the ghosts.</div>
<p class="note-small">Height = 4<br>Space = 5</p>
</div><div><TracePlayer example="kss4" /></div></div>

<!--
여기서 각 단계는 원고에 사용한 C++ 스케줄러에서 추출한 실제 trace다. 이후 block cleanup과 같은 H=4 트리와 같은 5개 레지스터 예산을 사용한다. 종료 시 root만 남고 ghost는 없어야 한다. Ghost-only actions are counted in steps, not work.
-->

---
layout: default
---

# Our idea: block clean

<BlockCleanupIdea />

<!--
KSS 뒤에 순차 block cleanup의 아이디어를 소개하는 개념도다. root는 출력으로 보존하고 왼쪽 subtree의 2,4,5를 정리할 영역으로 고른다. 각 root-to-leaf 경로를 가로지르는 8,9,10,11이 아래 경계다. 첫 화면에서 영역을 고르고, 다음 버튼으로 경계의 값을 모두 준비한다. 다음에는 경계를 유지하면서 4,5,2 순서로 값을 재계산하고 각 ghost의 위상을 보정한다. 마지막에는 2,4,5 순서로 uncompute하여 영역을 정리한다. 개념도는 각 준비 및 정리 과정을 한 화면으로 묶어 보여준다. 같은 경계값을 유지하여 여러 정점을 연속으로 정리하는 점이 핵심이다. 이후 경계를 해제하고 그 아래에 남은 ghost를 재귀적으로 정리한다. 이 그림은 특정 공간 예산에서 추출한 실행 trace가 아니며, 실제 H=4, 5-register 실행은 다음 장에서 보여준다. 내부 버튼으로 그림을 조작하고 방향키는 페이지 이동에 쓴다.
-->

---
layout: default
---

# Block cleanup in action

<div class="split-demo"><div>
<div class="lead small">Less recomputation</div>
<p>KSS &nbsp; 71 work<br>Ours &nbsp; <b>60 work</b></p>
<p class="note-small">Height = 4<br>Space = 5</p>
</div><div><TracePlayer example="sequential4" /></div></div>

<!--
위 수치는 현재 논문 코드의 실제 실행 결과이다. Ghosting은 순차 action으로 세지만 work에는 들어가지 않으므로 67 actions와 60 work는 서로 다르다. 이 한 예시는 점근적 최적성의 증명이 아니다.
-->

---
layout: default
---

# Why block cleanup saves work

<div class="cleanup-proof">
<div class="cleanup-comparison">
<div><h3>Layer cleanup</h3><p>1 level at a time</p><div class="layer-bars"><i></i><i></i><i></i><i></i><i></i><i></i></div></div>
<div><h3>Block cleanup</h3>

Group $\Theta(\log s)$ levels

<div class="block-bars"><i></i><i></i></div></div>
</div>
<div class="cleanup-cost">
<div>

$O(n)$ work per stage

<small>Lemma 3.1</small>
</div>
<span class="cost-times">×</span>
<div>

$O\!\left(\dfrac{H}{\log(s+1)}\right)$ stages

<small>Lemma 3.3</small>
</div>
<span class="cost-times">=</span>
<div>

$O\!\left(\dfrac{nH}{\log(s+1)}\right)$ work

<small>Theorem 3.4</small>
</div>
</div>
<div class="minimum-space-result">

At minimum space $s=H+1=\Theta(\log n)$,

$$
\boxed{W^*=\Theta\!\left(\frac{n\log n}{\log\log n}\right)}
$$

</div>
<div class="proof-reference">Our paper · Theorem 3.4 (upper bound) · Theorem 4.3 (matching lower bound)</div>
</div>

<!--
약 90초. 이 장은 처음 line의 reversible space 결과가 아니라 완전 이진 트리의 sequential spooky work 결과다. H는 트리의 층 수이고 n=2^H-1이다. KSS의 층별 cleanup은 각 단계에서 선형 work를 쓰며 O(H)번 반복되어 O(nH)=O(n log n)이다. Block cleanup은 경계값을 유지하여 여러 층을 한 번의 contraction에 포함한다.

경계가 m개면 자르는 높이가 약 log m이다. 공간을 위해 상단 2m-1개 값과 경계 준비 중의 공간을 함께 고려해야 한다. Lemma 3.1의 정확한 조건은 max{2m-1, h+m-ceil(log m)}<=b다. b=s-1은 출력 root를 보존한 뒤 남은 공간이다. 최소 공간 초반에는 큰 경계를 준비할 여유가 작으므로 모든 contraction이 처음부터 Theta(log s)층을 지우는 것은 아니다. Lemma 3.3은 이 초기 구간까지 포함해 O(1+H/log(b+1))단계임을 보인다. 구체적으로 m=2^{floor((log b)/2)}<=sqrt b를 비교 경계로 잡는다. 남은 높이가 b-m 이하가 되면 이 경계가 가능해서 이후 각 단계가 Theta(log b)층을 줄인다. b<2H일 때도 초기 단계 수는 최대 sqrt b=O(H/log(b+1))에 들어간다. 이 조건을 설명할 때 화면의 Group Theta(log s) levels는 이 전체 단계 분석의 직관으로 소개한다.

각 contraction의 work를 해당 subtree의 leaf에 균등하게 부과하면 leaf당 O(1)이다 (Lemma 3.1). 같은 재귀 단계의 subtrees는 서로 겹치지 않으므로 트리 전체에서는 O(n) work다. 각 leaf가 만나는 contraction 수가 O(H/log(s+1))이므로 Theorem 3.4의 upper bound를 얻는다. 최소 공간은 정확히 s=H+1이며 Theta(log n)이지 log n과의 수치적 등식은 아니다. 이를 대입하면 O(n log n/log log n)이다. 최적 work의 Theta 표기는 별도로 증명한 Theorem 4.3의 matching lower bound를 사용한다. 이 lower bound를 여기서 증명하는 것은 아니며 화면에 근거 정리를 표시한다.

현재 제출 PDF main.pdf에서 정리 번호를 확인했다. Lemma 3.1 (Cost of one-block cleanup), Lemma 3.3 (Stage bound for block cleanup), Theorem 3.4 (Work analysis of FastClean), Theorem 4.3 (Work lower bound). 주결과는 Theorem 1.1.
-->

---
layout: default
---

# Parallel spooky pebbling

<div class="split-demo"><div>
<div class="lead small">Disjoint registers → same round</div>
<p class="note-small">Compute / uncompute → ghost<br>Height = 3<br>Space = 4</p>
</div><div><TracePlayer example="parallel" /></div></div>

<!--
우리 병렬 forest-stage 알고리즘에서 직접 수집한 trace이다. 첫 단계에서는 정점과 그 입력을 포함한 active set이 겹치지 않아야 한다. 둘째 단계에서는 ghosting을 한다. 한 칸의 step은 개별 연산이 아니라 두 단계 round다. 한 단계에 여러 pebble 또는 ghost가 표시될 수 있다. Source: https://arxiv.org/abs/2510.08432
-->

---
layout: default
disabled: true
---

# KMRV: a path schedule

<div class="split-demo"><div>
<div class="lead small">Keep the endpoint.<br>Clear the path.</div>
<p class="note-small">Fixed anchor at 0<br>ℓ = 7 · 13 rounds</p>
</div><div><TracePlayer example="kmrv" /></div></div>

<!--
원래 KMRV의 설명은 고정 초기 pebble과 ℓ개의 추가 정점에서 terminal을 방문하고 모든 추가 정점을 정리하는 데 최적 2ℓ round를 사용한다. 이 구현 trace는 endpoint를 보존하므로 2ℓ−1 round다. 이 화면에서는 실제 입력 레지스터 준비와 최종 input cleanup을 제외한다. 따라서 논문의 6.2 전체 reduction 비교와 같은 비용으로 해석하면 안 된다.
Source: https://arxiv.org/abs/2510.08432; repository cli/kmrv.cpp kmrv_path.
-->

---
layout: default
---

# The complete-tree result

<div class="lead">At the minimum space, block cleanup reduces recomputation.</div>

| Schedule | Cost |
|:--|:--|
| KSS | $O(n\log n)$ steps |
| Block cleanup | $\Theta(n\log n/\log\log n)$ work |

<p class="note-small">Both use H + 1 registers on a complete tree with n = 2<sup>H</sup> − 1 nodes.<br>KSS steps include ghosting; work counts computations and uncomputations. The two counts differ by less than a factor of two.</p>
<div class="takeaway">The new work bound is asymptotically optimal.</div>

<!--
KSS의 steps에는 ghosting이 포함된다. 우리의 work는 pebble과 unpebble 횟수다. 두 convention은 완전한 schedule에서 최대 상수배만 차이 나므로 점근적 비교에 문제가 없다. 전체 feasible space에서 최적 work는 Theta(nH/log(s+1))다. 병렬 depth도 별도로 최적화하며, 어떤 budget에서는 최적 depth가 work만 최소화할 때보다 더 많은 work를 요구한다. Source: current manuscript, Theorems 1.1, 3.4, and 4.3.
-->

---
layout: default
---

# Associative reductions

<div class="lead">Same ordered inputs, different evaluation trees.</div>
<div class="columns-2">
<div><h3>KMRV</h3><p>Left-to-right prefix path</p><p class="order-example">((a₁ ⊕ a₂) ⊕ a₃) ⊕ a₄</p></div>
<div><h3>Our construction</h3><p>Balanced binary tree</p><p class="order-example">(a₁ ⊕ a₂) ⊕ (a₃ ⊕ a₄)</p></div>
</div>
<p class="note-small">H = 5–17 · same measured KMRV implementation budget · input preparation and cleanup included.</p>
<div class="takeaway">Our depth is lower for H = 7–17; work is comparable across the tested heights.</div>

<!--
이 비교에서 결합법칙으로 서로 다른 괄호 배치를 선택할 수 있다. 그래프가 다르므로 고정 그래프에서 알고리즘만 비교한 것이 아니다. KMRV의 작은 입력 예시에서는 우리 depth가 더 크다. 표는 논문 6.2의 조건과 일치한다.
-->

---
layout: default
---

# Application: elliptic-curve arithmetic

<div class="lead">Point-addition trees occur in a quantum discrete-logarithm algorithm.</div>

$$
|P_1\rangle |P_2\rangle |0\rangle
\longmapsto |P_1\rangle |P_2\rangle |F_p(P_1,P_2)\rangle
$$

<p>Each value stores three coordinates modulo a small prime. The function F<sub>p</sub> combines two values.</p>
<div class="takeaway">At KSS space, abstract work decreases by 31.14%–41.32% across four trees.</div>
<p class="note-small">Measured task: retain the root triple and clean all other values. Residue extraction and accumulation are excluded.</p>
<div class="source">Chevignard, Fouque &amp; Schrottenloher (CFS), 2026</div>

<!--
CFS의 실제 root에는 별도 연산이 있다. 논문의 수치는 root triple을 보존하는 공통 tree-evaluation 과제에서 계산한 추상적 pebbling work이며, 전체 ECDLP gate count 또는 물리적 시간의 감소율이 아니다.
Source: https://eprint.iacr.org/2026/280 and current manuscript Section 6.3.
-->

---
layout: default
---

# Takeaways

<div class="sequence ending">
<div><span class="sequence-num">01</span><h3>Spooky pebbling</h3><p>Trade quantum space for deferred corrections.</p></div>
<div><span class="sequence-num">02</span><h3>Block cleanup</h3><p>Reuse a boundary to reduce reconstruction.</p></div>
<div><span class="sequence-num">03</span><h3>Parallel scheduling</h3><p>Minimize depth and work separately.</p></div>
</div>
<div class="closing">Thank you</div>

<!--
전체 work-depth tradeoff at a fixed space budget와 일반 DAG 확장은 열린 문제다.
-->
