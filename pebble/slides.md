---
theme: '@slidev/theme-bricks'
title: 'Spooky pebble game'
info: 'A visual introduction to reversible and spooky pebbling on binary trees.'
colorSchema: light
transition: fade
mdc: true
fonts:
  sans: 'Noto Sans'
  serif: 'DM Serif Display'
  mono: 'Fira Code'
---

# Spooky pebble game

<div class="cover-subtitle">Optimal (Parallel) Spooky Pebbling<br>on Binary Trees</div>
<div class="cover-arxiv"><a href="https://arxiv.org/abs/2610.09434">arXiv:2610.09434</a></div>

<div class="cover-byline">Mingyu Lee · Sanghyun Lee · Kabgyun Jeong</div>

<!--
이번 발표는 처음 접하는 청중을 대상으로 한다. pebble game의 규칙을 설명한 뒤 KSS, block cleanup, KMRV를 실제 스케줄로 살펴본다. 15–20분을 기준으로 각 trace의 핵심 순간만 보여준다.
-->

---
layout: default
---

# About me

<div class="speaker-intro">
  <div class="speaker-photo">
    <img src="/speaker/mingyu-lee.png" alt="Mingyu Lee" />
  </div>
  <div class="speaker-bio">
    <div class="speaker-name">Mingyu Lee</div>
    <div class="speaker-university">Seoul National University</div>
    <div class="speaker-study">Computer Science &amp; Engineering<br>Double major in Mathematics</div>
    <a class="speaker-homepage" href="https://red1108.github.io/">red1108.github.io</a>
    <div class="speaker-team">
      <img src="/speaker/team-qst.png" alt="Team QST logo" />
      <span>Team QST</span>
    </div>
  </div>
</div>

<!--
서울대학교 컴퓨터공학 전공, 수학 복수전공. Team QST 소속이다. 홈페이지는 https://red1108.github.io/ 이다.
-->

---
layout: default
---

# 1D chain computation

<div class="computation-intro">
<div class="computation-chain">

$$
\begin{aligned}
&\sum_x\alpha_x|x\rangle|0\rangle|0\rangle\cdots|0\rangle\\
\xrightarrow{U_1}\;&\sum_x\alpha_x|x\rangle|f_1(x)\rangle|0\rangle\cdots|0\rangle\\
\xrightarrow{U_2}\;&\sum_x\alpha_x|x\rangle|f_1(x)\rangle|f_2(f_1(x))\rangle\cdots|0\rangle\\
\xrightarrow{U_3,\ldots,U_n}\;&\sum_x\alpha_x|x\rangle|f_1(x)\rangle\cdots
|f_n(f_{n-1}(\cdots f_1(x)\cdots))\rangle
\end{aligned}
$$

</div>
<div class="computation-reference">Optimal parallel depth (KMRV, EUROCRYPT 2026).</div>
<svg class="computation-pebble-chain" viewBox="0 0 760 110" role="img" aria-label="Five pebbles in a chain, starting with x, with successive arrows labeled f1, f2, f3, and f4.">
  <defs>
    <marker id="computation-chain-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#82999a" />
    </marker>
  </defs>
  <g v-for="i in 4" :key="`edge-${i}`">
    <line :x1="70 + (i - 1) * 155 + 26" y1="67" :x2="70 + i * 155 - 29" y2="67" marker-end="url(#computation-chain-arrow)" />
    <text class="function-label" :x="70 + (i - .5) * 155" y="42" text-anchor="middle">f<tspan class="function-index" baseline-shift="sub">{{ i }}</tspan></text>
  </g>
  <circle v-for="i in 5" :key="`pebble-${i}`" :cx="70 + (i - 1) * 155" cy="67" r="25" />
  <text class="input-label" x="70" y="67" text-anchor="middle" dominant-baseline="central">x</text>
</svg>
</div>

<!--
앞에서 계산한 값을 다음 연산의 입력으로 쓰는 예다. f_i는 계산기저 값을 받아 새 레지스터에 결과를 쓰는 연산이며, 표시한 식은 중첩 입력 전체에 선형적으로 작용한다. 마지막 줄은 중간값을 모두 보관한 forward computation이다.
KMRV는 Kahanamoku-Meyer, Ragavan, Van Kirk다. Parallel Spooky Pebbling Makes Regev Factoring More Practical, EUROCRYPT 2026, LNCS 16541, pp. 402–430. 링크는 https://link.springer.com/chapter/10.1007/978-3-032-25291-3_14 이다. 고정 초기 pebble 뒤에 n개 정점이 있는 경로에서 terminal을 방문하고 추가 정점을 모두 정리하는 데 최적 2n round, O(log n) pebbles를 달성한다. 화면의 optimal은 parallel depth에 대한 결과다.
-->

---
layout: default
---

# Two-input computation

<div class="computation-intro computation-binary">

$$
|a\rangle|b\rangle|0\rangle
\longmapsto |a\rangle|b\rangle|f(a,b)\rangle
$$

<h2>Example: repeated addition</h2>
<div class="computation-addition">

$$
|x_1\rangle\cdots|x_n\rangle|0\rangle
\longmapsto
|x_1\rangle\cdots|x_n\rangle|x_1+\cdots+x_n\rangle
$$

</div>
<div class="computation-scope">We study computations with binary-tree dependencies.</div>
<img class="binary-computation-figure" src="/figures/binary_pebbling_concept.png" alt="Binary-tree pebbling configuration from our paper, showing pebbles, ghosts, and the root goal." />
</div>

<!--
두 입력을 보존하는 out-of-place 연산이다. 덧셈에서는 두 부분합을 결합하는 연산을 반복해 전체 합을 만든다. 화면에는 입력과 전체 합을 저장하는 출력 레지스터를 표시하고, 계산 중 사용하는 보조공간은 생략했다. 보조공간은 계산 종료 시 정리한다. n>=2이며 각 레지스터는 표시한 값을 담기에 충분한 폭을 가진다. 이 사상도 입력들의 임의 중첩에 coherent하게 작용해야 한다. 이항연산의 입력을 각각 한 번씩 사용하는 고정 binary tree가 우리 논문의 계산 모델이다.
-->

---
layout: default
---

# Coherence and garbage

<div class="coherence-intro">
<div class="coherence-comparison">
<div class="coherence-column">
<h2>If we don't clean the garbage</h2>
<div class="coherence-state">

$$
|\Psi\rangle=\sum_x\alpha_x|x\rangle_X|g(x)\rangle_G|f(x)\rangle_F
$$

</div>
<div class="coherence-reduced">

$$
\begin{aligned}
&\rho_{XF}=\operatorname{Tr}_G\!\left(|\Psi\rangle\langle\Psi|\right)\\[12pt]
&=\sum_{x,x'}\alpha_x\alpha_{x'}^*
\underbrace{\langle g(x')|g(x)\rangle}_{\text{garbage overlap}}
|x,f(x)\rangle\langle x',f(x')|
\end{aligned}
$$

</div>
<div class="coherence-result">

If $\langle g(x')|g(x)\rangle=0$, the cross term vanishes.

</div>
</div>
<div class="coherence-column">
<h2>If we clean the garbage</h2>
<div class="coherence-state">

$$
|\Psi_{\mathrm{clean}}\rangle=\sum_x\alpha_x|x\rangle_X|0\rangle_G|f(x)\rangle_F
$$

</div>
<div class="coherence-reduced">

$$
\begin{aligned}
&\rho^{\mathrm{clean}}_{XF}=\operatorname{Tr}_G\!\left(|\Psi_{\mathrm{clean}}\rangle\langle\Psi_{\mathrm{clean}}|\right)\\[12pt]
&=\sum_{x,x'}\alpha_x\alpha_{x'}^*
\underbrace{\langle0|0\rangle}_{1}
|x,f(x)\rangle\langle x',f(x')|
\end{aligned}
$$

</div>
<div class="coherence-result">

Every cross term is preserved.

</div>
</div>
</div>
</div>

<!--
X는 보존하는 입력, G는 중간값을 저장한 garbage, F는 최종 출력이다. 각 g(x)는 정규화된 상태다. 위의 두 상태는 전체 XGF의 순수 상태를 나타낸다. 아래 식은 G를 사용하지 않을 때 입출력 XF의 reduced state다.
전체 density matrix를 전개하면 각 항에 |g(x)><g(x')|가 붙고, Tr(|a><b|)=<b|a>이므로 garbage overlap이 나온다. 계산기저의 garbage라면 이 값은 같은 비트열에서 1, 서로 다른 비트열에서 0이다. 서로 다른 garbage가 직교하면 그 입력들 사이의 off-diagonal term이 사라진다. 모든 입력에서 G를 같은 |0>으로 돌리면 모든 overlap이 1이 되어 원하는 coherent 입출력 상태가 보존된다.
반드시 |0>일 필요는 없고, 입력과 무관한 같은 정규화 상태로 분리되어도 된다. x에 의존하는 위상도 의도한 연산과 일치하도록 보정되어야 한다. 여기서 비교하는 것은 XF이며, F만 따로 측정하는 통계는 cleanup 전후 같다. 보조공간을 회수하면서 coherent 서브루틴의 종료 조건을 만족시키는 것이 다음 pebbling 모델의 목표다.
-->

---
layout: default
---

# Pebble game

<img class="pebble-photo" src="/figures/pebbles.png" alt="Six smooth pebbles" />

<PebbleRule />

<!--
네 정점의 line에서 직접 원을 클릭한다. 모든 원이 비어 있는 상태로 시작한다. 맨 왼쪽 start는 자유롭게 토글할 수 있고 나머지 정점은 바로 앞 정점이 pebbled일 때만 토글할 수 있다. Pebble은 저장된 값을 뜻한다. 성공한 toggle은 compute 또는 uncompute 한 번이므로 work가 1 증가한다. Peak는 Reset 이후 동시에 존재한 pebble 수의 최댓값이다. 목표는 final에만 돌을 남기는 것이다. Reset은 모든 돌을 비우고 work와 peak를 0으로 만든다.
-->

---
layout: default
---

# Pebbling a line

<div class="visual-intro simple-line-intro">
<div class="intro-line">Compute → keep the final value → uncompute</div>
<TracePlayer example="line-simple" intro intro-metrics />
</div>

<!--
약 90초. 가장 먼저 그래프가 계산의 의존성을 나타내는 모델임을 설명한다. 노드는 계산값이고 pebble은 그 값이 메모리에 존재한다는 뜻이다. 0번은 입력 의존성이 없는 첫 계산값이며 자유롭게 load하거나 uncompute할 수 있다. i→i+1 화살표는 이전 값이 다음 값의 입력이라는 뜻이다. 처음 3개 행동으로 계산을 설명하고, 끝까지 이동해 마지막 값만 보존하고 앞부분은 역순으로 정리하는 목표를 보여준다. 이 단순한 전략은 8개 값을 동시에 보관한다. Source: Craig Gidney, https://algassert.com/post/1905.
-->

---
layout: default
---

# Reversible pebbling on a line

<div class="space-limited-question"><strong>What happens if space is limited?</strong> we need more work! (of course)</div>

<div class="visual-intro reversible-line-intro">
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

<div v-click="1" class="measurement-result" style="position: relative">
<div class="measure-arrow">↓ <span>X-basis measurement · outcome m ∈ {0, 1}<sup>k</sup></span></div>

$$
\sum_x \alpha_x \textcolor{#a45f3e}{(-1)^{m\cdot f(x)}} |x\rangle
$$

<img class="measurement-ghost" src="/figures/measurement-ghost.svg" alt="Ghost" width="119.4375" height="107.1875" style="position: absolute; left: calc(50% + 150px); bottom: -21.75px; width: 119.4375px; height: 107.1875px; transform: translateX(100%)" />
</div>
<div v-click="2" class="ghost-summary">
<span class="small-stone stored"></span><span class="small-arrow">→</span><span class="small-stone deferred">G</span>
<span class="ghost-summary-text">Free the register.<br>Keep the string <em>m</em> classically.<br>We can correct the phase later.</span>
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

# Exorcise: Correcting the phase

<div class="correction-math exorcism-math">
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
<div class="exorcism-illustration">
<img class="exorcism-ghost" src="/figures/measurement-ghost.svg" alt="Ghost" />
<img class="exorcism-priest" src="/figures/exorcist.svg" alt="Priest holding a cross toward the ghost" />
</div>
<div class="exorcism-references">
<a href="https://arxiv.org/abs/1212.5069" target="_blank" rel="noopener noreferrer" title="Low-overhead constructions for the fault-tolerant Toffoli gate">Jones (2013)</a>
<span> · </span>
<a href="https://arxiv.org/abs/1709.06648" target="_blank" rel="noopener noreferrer" title="Halving the cost of quantum addition">Gidney (2018)</a>
</div>
</div>

<!--
약 90초. 직전 장에서 ghosting한 값의 입력 x가 다시 준비되어 있다고 가정한다. Fresh register는 재사용할 k큐비트 |0^k> 보조 레지스터다. U_f|x>|y>=|x>|y XOR f(x)> 로 정의한다. 첫 클릭에서 f(x)를 다시 계산한다. 두 번째 클릭에서는 결과 레지스터의 j번째 큐비트에 Z^{m_j}를 적용한다. Z(m)=⊗_j Z^{m_j}가 (-1)^{m·f(x)}를 한 번 더 곱하므로 기존 위상이 상쇄된다. 이 시점에서 ghost가 pebble로 바뀐다. 논문의 Peb는 이 재계산과 위상 보정을 함께 포함한다. 마지막 클릭에서 U_f^dagger로 보조 레지스터를 |0^k>으로 되돌리면 정점은 empty가 된다. 이는 별도의 Unp 동작이다. x가 여러 입력 레지스터를 뜻하면 재계산과 uncompute에는 이들이 모두 있어야 한다. Ghosting 자체는 이 입력들을 요구하지 않으므로 더 일찍 양자 메모리를 해제할 수 있다. Ghost의 측정 결과 m은 보정이 끝나면 버릴 수 있다.
Source: current manuscript, Section 2, ghosting and phase correction; https://algassert.com/post/1905.
Related measurement-assisted constructions: Cody Jones, Low-overhead constructions for the fault-tolerant Toffoli gate, Physical Review A 87, 022328 (2013), https://arxiv.org/abs/1212.5069. Craig Gidney, Halving the cost of quantum addition, Quantum 2, 74 (2018), https://arxiv.org/abs/1709.06648.
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

# Spooky pebbling on a line graph

<div class="visual-intro spooky-line-intro">
<div class="intro-line">We have new actions! Ghosting / Exorcising</div>
<div class="spooky-line-cost">

Space: $O(1)$, Work: $O(n^2)$

</div>
<TracePlayer example="line-spooky" intro />

</div>

<!--
약 2분. 원문의 constant-space GIF를 확인했다. 먼저 앞의 pebble을 만들고 뒤의 pebble을 ghost로 바꿔 두 pebble로 endpoint까지 진행한다. endpoint를 보존한 뒤 앞부분을 다시 sweep하고 가장 오른쪽 ghost부터 정리한다. 전체 trace를 모두 설명하지 말고, 15번째 행동 부근의 endpoint 보존 상태와 종료 상태를 slider로 보여준다. 원문의 GIF는 확률적으로 ghost가 남는 모델이며 ghost를 직접 제거하는 행동이 있다. 여기서는 현재 논문과 동일하게 매 ghosting에 보정 의무를 기록하고, ghost를 재계산하는 Peb와 별도의 Unp로 정리하도록 변환했다. 따라서 원문 GIF의 시간 숫자와 이 trace의 action 수를 동일시하지 않는다. Source: https://algassert.com/post/1905.
-->

---
layout: default
---

# Binary-tree dependencies (Recap)

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

<TracePlayer example="kss-root" class="root-computation-demo">
<template #code="{ step }">
<StepCode :clicks="step" />
</template>
</TracePlayer>

<!--
KSS는 Kornerup, Sadun, Soloveichik의 알고리즘이다. 제출 논문의 Algorithm 1, Bottom-up root computation SequentialPebble(T)를 pseudocode로 표시했다. Release(u)는 leaf이면 Unpebble(u), 내부 정점이면 Ghost(u)로 풀어 썼다. 실제 scheduler의 trace를 재생하며 각 행동에 대응하는 줄을 강조한다. 29개 action의 마지막에는 root가 남고 아래 내부 정점 2~7에 ghost가 있다. Source: submitted manuscript, Algorithm 1; https://doi.org/10.22331/q-2025-02-18-1636.
-->

---
layout: default
---

# Full KSS algorithm

<TracePlayer example="kss-cleanup" class="cleanup-computation-demo">
<template #code="{ step }">
<CleanupCode :step="step" />
</template>
</TracePlayer>

<!--
앞 장과 같은 Height 4, Space 5 트리다. SequentialPebble이 끝난 native trace의 29/81 상태에서 시작하며 root 1은 pebble, 2~7은 ghost, 8~15는 empty다. work와 peak는 전체 KSS 실행의 누적 수치이며 시작 work=23, peak=5다. 슬라이더와 Reset은 이 시작점으로 돌아온다. 전체 native trace는 81 actions, work 71로 끝난다.
왼쪽 KSS 호출에서 Pebble(T)는 이미 완료한 부분이다. Cleanup(T_2), Cleanup(T_3)을 재생한다. 밝은 강조는 현재 cleanup 호출에서 실행하는 줄이며 어두운 강조는 현재 호출을 포함하는 재귀 호출이다. Pebble 내부의 여러 연산은 이를 호출한 prepare-left 또는 prepare-right 줄에 대응한다. 이 매핑은 C++의 호출 순서를 따라가며 각 p/u/g 동작을 실제 native trace와 대조한다. 여기서는 leaf에 ghost를 남기지 않는 KSS 실행이므로 leaf cleanup은 즉시 반환한다. Correct(v)는 값을 재계산하고 위상을 보정하는 Peb 동작이다. Release는 leaf이면 Unpebble, 내부 정점이면 Ghost다.
-->

---
layout: default
---

# Block cleanup

<BlockCleanupIdea />

<!--
KSS 뒤에 순차 block cleanup의 아이디어를 소개하는 개념도다. root는 출력으로 보존하고 왼쪽 subtree의 2,4,5를 정리할 영역으로 고른다. 각 root-to-leaf 경로를 가로지르는 8,9,10,11이 아래 경계다. 첫 화면에서 영역을 고르고, 다음 버튼으로 경계의 값을 모두 준비한다. 다음에는 경계를 유지하면서 4,5,2 순서로 값을 재계산하고 각 ghost의 위상을 보정한다. 마지막에는 2,4,5 순서로 uncompute하여 영역을 정리한다. 개념도는 각 준비 및 정리 과정을 한 화면으로 묶어 보여준다. 같은 경계값을 유지하여 여러 정점을 연속으로 정리하는 점이 핵심이다. 이후 경계를 해제하고 그 아래에 남은 ghost를 재귀적으로 정리한다. 이 그림은 특정 공간 예산에서 추출한 실행 trace가 아니다. 다음 장에서 경계 구성 알고리즘을 설명한 뒤 실제 H=4, 5-register 실행을 보여준다. 내부 버튼으로 그림을 조작하고 방향키는 페이지 이동에 쓴다.
-->

---
layout: default
---

# Boundary expansion

<BoundaryExpansion :height="4" :size="6" />

<!--
제출 논문의 Algorithm 2, Constructing a balanced boundary Boundary(T,m)와 sequential.cpp의 build_boundary에 대응한다. H=4, 15개 정점의 완전 이진트리에서 m=6으로 설정했다. 초기 경계 {1}을 자식 쪽으로 밀어내며 왼쪽은 ceil(m/2), 오른쪽은 floor(m/2)로 나눈다. 초록색 집합은 재귀 처리 중의 임시 frontier이며 양자 레지스터 점유나 pebbling 실행을 나타내지 않는다. 왼쪽 호출, 오른쪽 호출, base case의 return, 집합의 union을 각 단계에 맞춰 강조한다. 최종 경계는 왼쪽부터 {8,9,5,12,13,7}이고 깊이는 2 또는 3이다. 각 root-to-leaf 경로를 정확히 한 번 가로지른다. 이 단계에서는 경계의 위치만 정하며, 값의 계산과 보존은 Contract 단계에서 수행한다.
Source: submitted manuscript, Algorithm 2; sequential.cpp, build_boundary.
-->

---
layout: default
---

# Block cleanup in action

<div class="split-demo"><div>
<div class="lead small">KSS &nbsp; 71 work<br>Ours &nbsp; <b>60 work</b></div>
<p class="demo-budget">Height = 4<br>Space = 5</p>
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
</div>

<!--
약 90초. 이 장은 처음 line의 reversible space 결과가 아니라 완전 이진 트리의 sequential spooky work 결과다. H는 트리의 층 수이고 n=2^H-1이다. KSS의 층별 cleanup은 각 단계에서 선형 work를 쓰며 O(H)번 반복되어 O(nH)=O(n log n)이다. Block cleanup은 경계값을 유지하여 여러 층을 한 번의 contraction에 포함한다.

경계가 m개면 자르는 높이가 약 log m이다. 공간을 위해 상단 2m-1개 값과 경계 준비 중의 공간을 함께 고려해야 한다. Lemma 3.1의 정확한 조건은 max{2m-1, h+m-ceil(log m)}<=b다. b=s-1은 출력 root를 보존한 뒤 남은 공간이다. 최소 공간 초반에는 큰 경계를 준비할 여유가 작으므로 모든 contraction이 처음부터 Theta(log s)층을 지우는 것은 아니다. Lemma 3.3은 이 초기 구간까지 포함해 O(1+H/log(b+1))단계임을 보인다. 구체적으로 m=2^{floor((log b)/2)}<=sqrt b를 비교 경계로 잡는다. 남은 높이가 b-m 이하가 되면 이 경계가 가능해서 이후 각 단계가 Theta(log b)층을 줄인다. b<2H일 때도 초기 단계 수는 최대 sqrt b=O(H/log(b+1))에 들어간다. 이 조건을 설명할 때 화면의 Group Theta(log s) levels는 이 전체 단계 분석의 직관으로 소개한다.

각 contraction의 work를 해당 subtree의 leaf에 균등하게 부과하면 leaf당 O(1)이다 (Lemma 3.1). 같은 재귀 단계의 subtrees는 서로 겹치지 않으므로 트리 전체에서는 O(n) work다. 각 leaf가 만나는 contraction 수가 O(H/log(s+1))이므로 Theorem 3.4의 upper bound를 얻는다. 최소 공간은 정확히 s=H+1이며 Theta(log n)이지 log n과의 수치적 등식은 아니다. 이를 대입하면 O(n log n/log log n)이다. 최적 work의 Theta 표기는 별도로 증명한 Theorem 4.3의 matching lower bound를 사용한다. 이 lower bound를 여기서 증명하는 것은 아니며 화면에 근거 정리를 표시한다.

현재 제출 PDF main.pdf에서 정리 번호를 확인했다. Lemma 3.1 (Cost of one-block cleanup), Lemma 3.3 (Stage bound for block cleanup), Theorem 3.4 (Work analysis of FastClean), Theorem 4.3 (Work lower bound). 주결과는 Theorem 1.1.
-->

---
layout: default
class: complete-tree-result
---

# The complete-tree result

<div class="lead">Complete tree with n = 2<sup>H</sup> − 1 nodes and H + 1 registers</div>

| Schedule | Work |
|:--|:--|
| KSS | $O(n\log n)$ |
| **Ours** | $\boldsymbol{\Theta(n\log n/\log\log n)}$ |

<div class="space-work-tradeoff">

$$
W(n,s)=\Theta\!\left(\frac{n\log n}{\log s}\right),\qquad H+1\le s\le n
$$

<div class="space-case">

Minimum space $s=H+1=\log_2(n+1)+1$.

</div>
<div class="space-case">

Full space $s=n\quad\Longrightarrow\quad W(n,n)=\Theta\!\left(\dfrac{n\log n}{\log n}\right)=\Theta(n)$.

</div>
<div class="space-work-reference">Theorem 1.1</div>
</div>

<!--
KSS의 steps에는 ghosting이 포함된다. 우리의 work는 pebble과 unpebble 횟수다. 두 convention은 완전한 schedule에서 최대 상수배만 차이 나므로 점근적 비교에 문제가 없다. 전체 feasible space에서 최적 work는 Theta(nH/log(s+1))다. 병렬 depth도 별도로 최적화하며, 어떤 budget에서는 최적 depth가 work만 최소화할 때보다 더 많은 work를 요구한다. Source: current manuscript, Theorems 1.1, 3.4, and 4.3.
일반 공간 s에서의 식은 논문 Theorem 1.1의 Theta(nH/log(s+1))를 H=Theta(log n), log(s+1)=Theta(log s)로 바꿔 쓴 것이다. 최소 공간은 정확히 H+1=log2(n+1)+1이며 표는 이 경우의 비교다. s=n이면 모든 정점을 한 번씩 계산하고 root를 제외한 정점을 위에서 아래로 uncompute할 수 있어 2n-1 work다. 일반식도 Theta(n log n/log n)=Theta(n)으로 이 경우와 일치한다.
-->

---
layout: default
---

# Work comparison with KSS

<div class="lead small">Space budget: <em>H</em> + 1</div>

<img class="result-plot" src="/figures/sequential-work-and-memory.svg" alt="Across heights 5 through 17, block cleanup uses less work and keeps more registers occupied on average than KSS. The work reduction reaches 57.67 percent at height 17." />

<!--
왼쪽에서 회색 KSS와 파란색 block cleanup의 work를 로그축으로 비교한다. 초록 점선은 오른쪽 축으로 읽는다. KSS 대비 절감률은 H=5의 25.65%에서 H=17의 57.67%까지 전반적으로 커진다. 오른쪽 패널은 같은 공간 한도에서 실행 중 평균적으로 레지스터를 얼마나 채웠는지 보여준다. H=17에서 두 방법의 한도는 18개이고, 평균 점유율은 KSS 37.81%, block cleanup 49.45%다. 경계값을 유지하면 나중에 다시 계산할 일이 줄어든다.
출처는 ACM 제출본 6.1절의 numerical_tradeoffs.pdf다.
-->

---
layout: default
---

# Parallel computation

<img class="parallel-computation-circuit" src="/figures/parallel-computation.svg" alt="Eight-qubit circuit with eight CCZ gates grouped into four parallel depths. Gates within each depth act on disjoint qubits." />

<div class="parallel-computation-explanation">
<p>In principle, gates on disjoint qubits can run simultaneously.</p>
<p>Parallel depth models the execution time.</p>
</div>

<!--
8큐비트, 8개 CCZ 연산을 4개 depth로 묶은 예다. Depth 1은 CCZ(1,2,5)와 CCZ(3,4,8), Depth 2는 CCZ(2,7,8)와 CCZ(3,5,6)이다. 추가한 Depth 3은 CCZ(1,4,7)와 CCZ(2,5,6), Depth 4는 CCZ(1,3,6)와 CCZ(4,5,8)이다. 각 depth 내부의 두 연산은 사용하는 큐비트가 겹치지 않는다. 세 filled dot을 연결한 것이 CCZ 하나이며, 수평 wire와 교차하더라도 dot이 없는 큐비트는 해당 연산에 포함되지 않는다.

같은 depth 안의 게이트 두 개는 세로 제어선이 겹쳐 하나의 게이트로 보이는 것을 피하기 위해 가로로 어긋나게 그렸다. 색칠한 한 영역 전체가 하나의 depth다. 이 예시는 CCZ를 한 단위시간의 primitive로 취급하고 서로 다른 큐비트에 대한 연산을 동시에 실행할 하드웨어 자원을 가정한다. 실제 wall-clock 시간은 native gate 분해, 연결성, gate duration, 제어 자원 등의 영향도 받는다. 이 가정 아래 serial gate count는 8, parallel depth는 4다. 가능한 양자컴퓨터의 병렬 실행을 이론적으로 모델링하는 목적이라고 설명한 뒤 다음 장의 disjoint active sets로 연결한다.

회로는 LaTeX Quantikz로 작성했다. 소스는 scripts/parallel_computation.tex, 재생성 명령은 bash scripts/build_parallel_circuit.sh다. Quantikz documentation: https://ctan.org/pkg/quantikz.
-->

---
layout: default
class: kmrv-line-demo
---

# KMRV on a line graph

<div class="kmrv-line-cost">

$n=16$ · Space: $O(\log n)$ · Depth: $2n-1$

</div>
<TracePlayer example="kmrv16" folded-path />
<div class="kmrv-line-reference"><a href="https://arxiv.org/abs/2510.08432">KMRV · EUROCRYPT 2026</a></div>

<!--
KMRV Algorithms 2.2 and 2.3 blast/unblast implementation, cli/kmrv.cpp. n denotes the 16 edges / computed vertices 1–16 after the fixed anchor 0, so there are 17 circles. The original visit-and-clean task has depth 2n. Here the endpoint is retained by omitting its final uncomputation, giving exactly 2n-1=31 rounds. This is depth, not work. The counters show actual computations and uncomputations, including parallel jobs in one round. Ghosting is zero work in our manuscript convention. Path layout folds once at the right; arrows continue from 8 to 9 and return to 16 at bottom left. Highlighted operations in the same frame execute in the same round.
Source: https://arxiv.org/abs/2510.08432, Algorithms 2.2–2.3; native kmrv_path(16).
-->

---
layout: default
---

# Parallel cleanup

<ParallelForestIdea />

<!--
약 40초. 높이 5인 전체 트리 31정점을 고정하고, 한 batch에서 실제 정리할 block과 그 입력을 유지하는 boundary를 표시한다. 모든 정점의 번호를 적고 caption에 Clear 대상으로 명시한다. 위치와 모양은 끝까지 동일하다. 출력 root는 트리 맨 위에 보존한다. 처음에는 parallel root computation이 끝난 상태로 root 1만 pebble이고 2~31은 모두 ghost다. 각 다음 버튼으로 현재 block의 작업을 마치면 그 block의 ghost가 사라지고 다음 batch를 강조한다. 정리된 정점은 빈 원으로 남겨 전체 트리 위치를 유지한다. 개별 round가 아니라 batch 전후의 상태를 나타내는 개념도이며, 다음 실제 trace 페이지에서 세부 동작을 보여준다.

Algorithm 6의 H=5, s=9, cleanup 공간 b=8인 예시다. 먼저 높이 4인 두 subtree T_2와 T_3를 a=1,c=8로 하나씩 처리한다. 최대 feasible cut은 k=2이므로 각 subtree의 위쪽 두 층을 정리한 뒤 높이 2인 subtree 여덟 개 T_8,...,T_15가 남는다. 그다음 p(2)=3이고 a=floor(8/3)=2,c=4이므로 [8,9], [10,11], [12,13], [14,15]를 두 개씩 동시에 정리한다. 이들은 전체 3정점이 각 할당 공간에 들어가므로 terminal cleanup이다. 처음에는 2,4,5 block을 강조하고 8,9,10,11 boundary를 금색으로 표시한다. 다음에는 3,6,7 block과 12,13,14,15 boundary다. 이후 높이 2인 terminal job들은 세 정점 전체를 정리하므로 해당 정점들을 모두 강조한다. 서로 다른 색의 두 영역은 동시에 수행하는 독립 job이다. 마지막은 강조 영역이 없어지고 root만 출력으로 보존된다. 경계의 금색 표시는 다음 작업에 사용할 boundary 위치다. 준비 단계에서 해당 값을 재계산해 유지하고, block 정리가 끝나면 내부 boundary root를 다시 ghost로 해제하므로 그 아래 ghost들은 다음 batch까지 남는다. leaf를 포함한 모든 초기 ghost가 마지막 batch 뒤에는 제거된다.

큰 subtree를 하나씩 처리한 뒤 작은 subtree에 공간을 다시 나눠 두 개씩 처리한다는 아이디어를 설명한다. 예전 H=9의 메모리 막대와 동적으로 재배치한 forest 대신 전체 의존성 트리를 고정하여 설명한다. 모든 준비와 정리 동작을 한 round에 수행한다는 뜻은 아니며, 각 영역에서의 block contraction을 한 개념 단계로 표시한다.
Source: Algorithm 6 and equations (10)–(11) of our paper.
-->

---
layout: default
---

# Parallel spooky pebbling

<div class="split-demo"><div>
<div class="lead small">Operations on disjoint registers run in parallel.</div>
<p class="demo-budget">Height = 4<br>Space = 5</p>
</div><div><TracePlayer example="parallel4" /></div></div>

<!--
우리 병렬 forest-stage 알고리즘에서 직접 수집한 trace이다. 첫 단계에서는 정점과 그 입력을 포함한 active set이 겹치지 않아야 한다. 둘째 단계에서는 ghosting을 한다. 한 칸의 step은 개별 연산이 아니라 두 단계 round다. 한 단계에 여러 pebble 또는 ghost가 표시될 수 있다. Source: our paper, Algorithm 6; native C++ trace at commit d508128
-->

---
layout: default
class: parallel-analysis
---

# Complexity analysis: Memory per subtree

<div class="analysis-context">

Height $h$ · budget $b\ge h+1$

</div>
<div class="subtree-cost">

$$
D_{\mathrm{block}}=O\!\left(h+\frac{2^h}{b}\right)
$$

</div>
<div class="block-cost-explanation">

Dependencies require at least $h$ rounds, while $\Theta(2^h)$ node evaluations at $O(b)$ per round give the $2^h/b$ term.

</div>
<div class="target-budget">

$$
b\ge p(h)=\Theta\!\left(\frac{2^h}{h}\right)
\quad\Longrightarrow\quad
D_{\mathrm{block}}=O(h)
$$

</div>
<div class="analysis-reference">Lemma 3.6 · Target budget in equation (10)</div>

<!--
약 35초. 이 페이지는 원고 Lemma 3.6처럼 h를 한 subtree의 높이, b를 이 subtree에 할당한 register 수로 쓴다. 다음 페이지에서는 같은 메모리 배분 논의를 남은 높이 t와 job별 할당량 c로 표현한다. Lemma 3.6이 주는 한 번의 block contraction depth는 O(h+2^h/b)이며 feasible cut이 전제다. 재귀적으로 남은 subtree들을 모두 정리한 전체 depth가 아니라 한 block을 처리하는 비용이다.

문장은 두 항의 병목 직관을 설명한다. dependency chain을 따라가려면 높이에 비례하는 rounds가 필요하다. 평가할 정점은 2^h-1=Theta(2^h)개이고 한 round에서 b개 registers로 동시에 처리 가능한 연산 수는 O(b)이므로 throughput에 따른 2^h/b 항이 나타난다. 이 두 병목은 필요한 시간의 하한을 직관적으로 설명하며, 이를 상한으로 달성한다는 사실은 별도로 증명한 Sweep와 parallel block-cleanup 분석 (Lemmas 3.5–3.6)에 근거한다. 매 round가 균일하게 b개의 연산을 수행한다고 가정하는 것은 아니고 전체 스케줄을 상각 분석한다.

target p(h)는 정확히 max{h+1,ceil(2^h/h)} (h>=2), p(1)=1이다. 따라서 p(h)=Theta(2^h/h)이고 b>=p(h)이면 이 subtree의 block을 O(h) rounds에 처리할 수 있다. 남은 메모리는 다른 독립 subtree를 동시에 실행하는 데 배분한다. bounded height에서 feasibility를 보장하는 max 항은 말로 설명한다.
Source: Lemmas 3.5–3.6; equation (10).
-->

---
layout: default
class: parallel-analysis regime-height-detail
---

# Complexity analysis: Two cleanup regimes

<div class="analysis-context">

Current subtree height $h$ · cleanup space $b=s-1$

</div>
<div class="cleanup-regimes">
<div>
<h3>Space-limited</h3>

$b<p(h)$

One subtree per batch, $c=b$

$$
O\!\left(\frac{H}{\log(b+1)}\right)\text{ stages}
$$

</div>
<div>
<h3>Space-rich</h3>

$b\ge p(h)$

Per subtree $c\ge p(h)$

Can clear $t=h-\log_2 h-O(1)$ levels.

$$
2^t\asymp \frac{2^h}{h}
$$

$$
\underbrace{h}_{\text{current height}}
\;\longrightarrow\;
\underbrace{h-t=O(\log h)}_{\text{remaining height}}
$$

$$
O(1+\log^*H)\text{ stages}
$$

</div>
</div>
<div class="analysis-reference">Lemma 3.3 · Theorem 3.7 proof</div>

<!--
약 45초. H는 원래 전체 트리 높이, h는 현재 subtree 높이, t는 한 stage에서 정리하는 block의 층수다. 공간이 부족한 구간에서는 p(h)>b라 한 번에 한 subtree만 처리하고 c=b를 준다. 가능한 가장 큰 cut을 선택한다. 특히 최소 공간 초반에는 cut이 얕을 수 있다. 모든 stage가 처음부터 Theta(log b)층을 제거한다고 말하지 않는다. Lemma 3.3이 초기 구간을 포함한 전체 stage 수 O(H/log(b+1))를 준다.

p(h)<=b가 되면 a=min{A,floor(b/p(h))}개 subtree를 동시에 실행하고 각자 c=floor(b/a)>=p(h)를 받는다. A가 작으면 a=A다. 공간을 균등하게 재배분하므로 남은 forest의 높이도 공통으로 유지된다. 이후 p(h)는 높이가 줄수록 감소하므로 space-rich 조건은 유지된다.

높이 h에서 t=h-ceil(log2 h)-2개 층을 정리하는 cut을 고려한다. 경계 m=2^t=Theta(2^h/h)이고 남은 높이는 h-t=ceil(log2 h)+2다. 충분히 큰 h에서 m,h-t<=2^h/(4h)이므로 m+(h-t)<=c와 2m-1<=c를 동시에 만족한다. 따라서 화면의 t=h-log2 h-O(1)개 층을 실제로 정리할 수 있다. 알고리즘은 가장 깊은 feasible cut을 택하므로 실제 남은 높이는 이보다 클 수 없다. h→O(log h)를 반복하면 O(1+log*H) stages다. 상수 높이는 별도의 상수 개 terminal stages로 처리한다.
Source: Lemma 3.3; proof of Theorem 3.7.
-->

---
layout: default
class: parallel-analysis
---

# Complexity analysis: Depth of one stage

<div class="analysis-context">

Space-rich stage · height $h$

</div>
<div class="stage-cancellation">

$$
\underbrace{\frac{n/2^h}{bh/2^h}}_{\text{batches}}
\cdot
\underbrace{h}_{\text{rounds per batch}}
=\frac nb
$$

</div>
<div class="stage-critical-path">

One batch still takes $O(h)$ rounds.

$$
D_{\mathrm{stage}}=O\!\left(h+\frac nb\right)
$$

</div>
<div class="analysis-reference">Equation (14)</div>

<!--
약 40초. 먼저 space-rich 구간의 cancellation 직관을 설명한다. 한 subtree에는 Theta(2^h)개 정점이 있고, 전체 subtree 수는 A=Theta(n/2^h)다. subtree 하나에 p(h)=Theta(2^h/h) registers를 주면 O(h) rounds에 처리한다. 동시 처리 용량은 대략 b/p(h)=Theta(bh/2^h)개다. 용량이 A보다 작을 때 batch 수×batch당 depth가 n/b로 상쇄된다. 실제 batch 수는 적어도 하나이므로 critical-path O(h) 항이 추가된다. floors와 A에 의한 cap은 이 O(h+n/b) 안에 포함된다.

전체 regime에 통일된 식 (14)의 증명은 a개 동시 job, c=floor(b/a), A개 총 job에서 O((A/a)(h+2^h/c))=O(A*h/a+A*2^h/b)로 쓴다. target 선택이 A*h/a=O(h+n/b)를 보장하고 A*2^h=O(n)이다. space-limited에서도 a=1,c=b이고 p(h)>b 및 b>=h+1로부터 h<=O(n/b)여서 이 식이 성립한다. 화면에는 space-rich 계산만 두고, 같은 bound가 두 구간에 적용된다는 점을 말로 연결한다.
Source: equation (14), forest-stage depth, in the proof of Theorem 3.7.
-->

---
layout: default
class: parallel-analysis parallel-upper-sum
---

# Complexity analysis: Parallel depth upper bound

| Regime | Total depth |
|:--|:--|
| Space-limited | $O\!\left(\dfrac{nH}{b\log(b+1)}\right)$ |
| Space-rich | $O\!\left(H+\dfrac{n(1+\log^*H)}b\right)$ |

<div class="budget-substitution">

$b=s-1=\Theta(s)$

</div>

$$
D=O\!\left(H+\frac ns\left(\frac H{\log(s+1)}+1+\log^*H\right)\right)
$$

<div class="analysis-reference">Theorem 3.7</div>

<!--
약 40초. 공간 부족 구간에서는 O(H/log(b+1)) stages이고 매 stage의 depth가 O(n/b)여서 첫 행을 얻는다. 공간 여유 구간에서는 stage 수 O(1+log*H), 각 stage depth O(t+n/b)다. 남은 높이가 t→ceil(log t)+2로 줄어들므로 높이들의 합은 O(H)이며, 이를 매 stage의 H로 상계해서 H log*H를 붙이지 않도록 주의한다. 따라서 둘째 행은 O(H+n(1+log*H)/b)다.

첫 root computation Sweep(H,s)는 O(H+n/s) depth다. 이를 함께 더하고 b=s-1=Theta(s), log b=Theta(log(s+1))를 사용하면 Theorem 3.7의 upper bound다. 다음 최적 depth 페이지의 max{H/log(s+1),1+log*H}와 여기의 두 항의 합은 최대 상수 2배 차이이므로 같은 asymptotic order다. 전체 feasible range에서는 depth-optimal schedule의 work가 work-optimal schedule보다 더 클 수 있으며, 이 분석이 두 최적값의 동시 달성을 주장하는 것은 아니다.
Source: Theorem 3.7; main optimal-depth result Theorem 1.1.
-->

---
layout: default
class: parallel-depth-result
---

# Complexity analysis: Optimal parallel depth

<div class="parallel-minimum-space">

Complete tree $n=2^H-1$ · minimum space $s=H+1$

</div>

| Schedule | Depth (Time) |
|:--|:--|
| KSS (sequential) | $O(n\log n)$ |
| Ours (sequential) | $\Theta(n\log n/\log\log n)$ |
| **Ours (parallel)** | $\boldsymbol{\Theta(n/\log\log n)}$ |

<div class="parallel-general-depth">

For every space budget $H+1\le s\le n$,

$$
D^*(n,s)=\Theta\!\left(H+\frac ns\max\!\left\{\frac{H}{\log(s+1)},1+\log^*H\right\}\right)
$$

At full space $s=n$, $D^*(n,n)=\Theta(H)=\Theta(\log n)$.

</div>
<div class="parallel-result-reference">Our paper · Theorems 1.1, 3.7 · Lower bounds in Section 5</div>

<!--
약 1분. 동일한 완전 이진트리 n=2^H-1, 동일한 최소 공간 s=H+1에서 순차 KSS와 우리 순차·병렬 실행의 시간을 비교한다. 표의 KSS 행은 순차 전략을 매 동작 한 라운드로 실행한 상한 O(n log n)이다. 기존 병렬 binary-tree 알고리즘의 최적 하한으로 해석하지 않는다. KSS는 Theorem 5.5, Quantum 9, 1636 (2025)에서 이 순차 상한을 준다. 우리 순차 실행은 work와 전체 action 수가 상수배 관계라 depth도 Theta(n log n/log log n)이다. 최소 공간에서는 한 병렬 구성으로 work Theta(n log n/log log n), depth Theta(n/log log n)를 동시에 달성한다.

일반 공간에서의 정확한 최적 depth는 제출 논문 Theorem 1.1의 식 (2)다. Theorem 3.7의 상한은 O(H+nH/(s log(s+1))+n lambda(H)/s)이고 두 양의 항의 합은 최댓값과 상수배로 동치다. Section 5의 critical-path, work/space, cumulative-storage 하한이 일치한다. H는 vertex 층 수, log* H는 1 이하가 될 때까지 이진 로그를 반복하는 횟수다. s=H+1이면 H/log H가 lambda(H)보다 점근적으로 커 depth Theta(n/log H)=Theta(n/log log n)이다. s=n이면 H 항이 지배적이므로 Theta(H)=Theta(log n)이다. 일반 공간에서는 work 최적화와 depth 최적화를 각각 수행하며, 두 최적값을 항상 같은 schedule이 달성한다는 주장은 하지 않는다.

KMRV의 parallel 경로 결과는 다른 dependency graph에 대한 결과다. 결합법칙으로 그래프를 선택할 수 있는 application 비교는 이어지는 Associative reductions와 Depth comparison with KMRV 두 장에서 다룬다.
Source: submitted manuscript, Theorem 1.1, Theorem 3.7, Section 5; KSS, https://doi.org/10.22331/q-2025-02-18-1636.
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

# Associative reductions

<div class="lead">Associativity → freedom to choose the evaluation order</div>
<div class="columns-2">
<div><h3>KMRV</h3><p>Left-to-right prefix path</p><p class="order-example">((a₁ ⊕ a₂) ⊕ a₃) ⊕ a₄</p></div>
<div><h3>Our construction</h3><p>Balanced binary tree</p><p class="order-example">(a₁ ⊕ a₂) ⊕ (a₃ ⊕ a₄)</p></div>
</div>

<div class="shape-optimality">
Our balanced-tree construction is asymptotically optimal over all binary evaluation trees at the same space budget.
</div>

<!--
결합법칙으로 입력 순서를 보존하면서 서로 다른 괄호 배치를 선택할 수 있다. 왼쪽은 prefix path, 오른쪽은 balanced tree다. 두 방식의 병렬 라운드 수를 다음 장에서 비교한다.
-->

---
layout: default
---

# Depth comparison with KMRV

<div class="lead small">Both schedules use the same register budget at each height.</div>

<img class="result-plot" src="/figures/associative-reduction-depth.svg" alt="The balanced tree is slightly deeper than the KMRV prefix path at heights 5 and 6, then shallower from heights 7 through 17. At height 17 depth falls from 205,370 to 94,824 rounds." />

<!--
H=5–17에서 KMRV 구현이 실행 가능한 최소 레지스터 수를 구해 두 스케줄에 같은 예산을 준다. 두 스케줄 모두 입력 준비와 정리를 포함한다. 왼쪽 로그축은 라운드 수이고, 오른쪽 축의 초록 점선은 KMRV 대비 depth 절감률이다. H=5,6에서는 우리 쪽이 조금 더 깊고 H=7부터 더 얕다. H=17에서는 두 스케줄 모두 레지스터 37개를 사용하며, depth는 205,370에서 94,824로 줄어든다. 절감률은 53.83%다. Work는 실험 범위에서 비슷하다.
출처는 ACM 제출본 6.2절의 associative_reduction_depth.pdf와 Table 1이다.
-->

---
layout: default
class: cfs-application
---

# Elliptic-curve point-addition trees

<div class="cfs-context">

CFS attacks $n$-bit ECC using $\widetilde O(n^4)$ gates and $3.12n+o(n)$ logical qubits.

</div>

<div class="cfs-operation">

Point addition on triples $P=(X,Y,Z)$: $\quad\lvert P_1\rangle\lvert P_2\rangle\lvert 0\rangle\longmapsto\lvert P_1\rangle\lvert P_2\rangle\lvert F_p(P_1,P_2)\rangle$.

</div>

<div class="lead small">31–41% less work at the same register budget.</div>

| Curve | Registers | KSS work | Ours |
|:--|--:|--:|--:|
| P-224 | 7 | 203 | 135 |
| P-256 | 7 | 238 | 159 |
| P-384 | 7 | 395 | 272 |
| P-521 | 8 | 547 | 321 |

<!--
Chevignard, Fouque, and Schrottenloher의 양자 이산로그 알고리즘에서 쓰는 네 개의 점 덧셈 트리다. 각 pebble은 작은 소수 p를 법으로 하는 좌표 세 개를 저장한다. 같은 레지스터 예산에서 루트의 좌표를 남기고 나머지 값과 ghost를 모두 지우는 데 필요한 계산과 역계산 횟수를 비교한다. 절감 범위는 31.14%–41.32%다. CFS 알고리즘에서 뒤이어 수행하는 residue extraction과 accumulation은 이 수치에 포함되지 않는다.
Source: https://eprint.iacr.org/2026/280 and current manuscript Section 6.3, Table 2.
-->

---
layout: default
---

# Open questions

<div class="lead small">At fixed space, what is the full work–depth tradeoff for complete binary trees?</div>

<div class="lead small">Can we extend block cleanup to DAGs with shared values and prove tight bounds?</div>

<!--
Theorem 5.2에서 s=Theta(n/H)이면 최소 work는 Theta(n)이지만, 최적 depth를 달성하려면 Theta(n(1+log* H)) work가 필요하다. 고정된 공간 예산에서 가능한 work와 depth의 전체 관계는 열린 문제다.
트리에서는 중간값이 한 부모에게만 전달된다. 여러 연산이 같은 중간값을 입력으로 쓰면 의존성이 일반 DAG를 이룬다. 이 경우에도 block cleanup을 적용할 수 있는지, 그리고 work와 depth에 대해 일치하는 상한과 하한을 얻을 수 있는지가 두 번째 질문이다.
출처는 ACM 제출본 7절 Discussion이다.
-->
