# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Private, immutable epistemic reference context for W1A and W1B.

This module is an internal overlay over :class:`ValidatorInput`.  It preserves
claim, reference, dependency, temporal, and admissibility information that the
public input contract cannot currently express.  W1B retains declared,
claim-bound presence and agent-access findings; it does not discover presence
or access, assess absence evidence, or certify the findings.  Point-in-time
views preserve all matching findings, including unresolved and conflicting
ones.  There is no truth, independence, sufficiency, causality, evaluator, or
state-machine integration.

Nothing in this module is re-exported from :mod:`rpf_validator`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TypeAlias

from rpf_validator.models import ValidatorInput


_INPUT_OBSERVATION_ID = "validator-input-observation"


class ReferenceContextError(ValueError):
    """Raised when an internal reference context is structurally inconsistent."""


def _non_empty(value: object, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReferenceContextError(f"{path} must be a non-empty string")


def _tuple(value: object, item_type: type[object], path: str) -> None:
    if not isinstance(value, tuple):
        raise ReferenceContextError(f"{path} must be a tuple")
    for index, item in enumerate(value):
        if not isinstance(item, item_type):
            raise ReferenceContextError(
                f"{path}[{index}] must be {item_type.__name__}"
            )


def _aware(value: object, path: str) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ReferenceContextError(f"{path} must be a timezone-aware datetime")


def _instant_key(value: datetime) -> int:
    """Compare validated aware instants without materializing a UTC datetime.

    Integer microseconds preserve precision beyond datetime's UTC bounds.
    The actual UTC offset retains distinctions between local DST folds.
    """

    offset = value.utcoffset()
    assert offset is not None  # The caller already validated an aware datetime.
    local_microseconds = (
        (value.toordinal() * 86_400 + value.hour * 3_600
         + value.minute * 60 + value.second) * 1_000_000
        + value.microsecond
    )
    offset_microseconds = (
        (offset.days * 86_400 + offset.seconds) * 1_000_000 + offset.microseconds
    )
    return local_microseconds - offset_microseconds


class ClaimNamespace(StrEnum):
    """Small internal namespace separating the three supported claim anchors."""

    HYPOTHESIS = "hypothesis"
    OBSERVATION = "observation"
    INTERNAL = "internal"


class ReferenceNamespace(StrEnum):
    """Separate declared input sources from candidates, without proving presence."""

    EVIDENCE_SOURCE = "evidence-source"
    CANDIDATE = "candidate"


@dataclass(frozen=True, slots=True)
class ClaimId:
    """A case-local claim identifier with an explicit internal namespace."""

    namespace: ClaimNamespace
    local_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.namespace, ClaimNamespace):
            raise ReferenceContextError("claim_id.namespace must be ClaimNamespace")
        _non_empty(self.local_id, "claim_id.local_id")
        if (
            self.namespace is ClaimNamespace.OBSERVATION
            and self.local_id != _INPUT_OBSERVATION_ID
        ):
            raise ReferenceContextError(
                "the ValidatorInput observation has one deterministic claim handle"
            )

    @classmethod
    def hypothesis(cls, hypothesis_id: str) -> ClaimId:
        return cls(ClaimNamespace.HYPOTHESIS, hypothesis_id)

    @classmethod
    def observation(cls) -> ClaimId:
        return cls(ClaimNamespace.OBSERVATION, _INPUT_OBSERVATION_ID)

    @classmethod
    def internal(cls, claim_id: str) -> ClaimId:
        return cls(ClaimNamespace.INTERNAL, claim_id)


@dataclass(frozen=True, slots=True)
class ReferenceId:
    """A case-local reference identifier with an explicit internal namespace."""

    namespace: ReferenceNamespace
    local_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.namespace, ReferenceNamespace):
            raise ReferenceContextError(
                "reference_id.namespace must be ReferenceNamespace"
            )
        _non_empty(self.local_id, "reference_id.local_id")

    @classmethod
    def evidence_source(cls, source_id: str) -> ReferenceId:
        return cls(ReferenceNamespace.EVIDENCE_SOURCE, source_id)

    @classmethod
    def candidate(cls, candidate_id: str) -> ReferenceId:
        return cls(ReferenceNamespace.CANDIDATE, candidate_id)


@dataclass(frozen=True, slots=True)
class TargetId:
    """Opaque identifier for a claimed world state or other case-local target."""

    local_id: str

    def __post_init__(self) -> None:
        _non_empty(self.local_id, "target_id.local_id")


class ScopeSource(StrEnum):
    """Whether a scope is local or references the existing input frame scope."""

    REFERENCE_FRAME = "reference-frame"
    LOCAL = "local"


@dataclass(frozen=True, slots=True)
class ClaimScope:
    """Minimal claim-scope binding without a scope ontology."""

    source: ScopeSource
    text: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source, ScopeSource):
            raise ReferenceContextError("claim_scope.source must be ScopeSource")
        if self.source is ScopeSource.REFERENCE_FRAME:
            if self.text is not None:
                raise ReferenceContextError(
                    "reference-frame scope must not duplicate scope text"
                )
        else:
            _non_empty(self.text, "claim_scope.text")

    @classmethod
    def reference_frame(cls) -> ClaimScope:
        return cls(ScopeSource.REFERENCE_FRAME)

    @classmethod
    def local(cls, text: str) -> ClaimScope:
        return cls(ScopeSource.LOCAL, text)


@dataclass(frozen=True, slots=True)
class ClaimAnchor:
    """Enroll one claim in W1A without duplicating existing model content."""

    claim_id: ClaimId
    internal_statement: str | None = None
    target_id: TargetId | None = None
    scope: ClaimScope | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.claim_id, ClaimId):
            raise ReferenceContextError("claim.claim_id must be ClaimId")
        if self.claim_id.namespace is ClaimNamespace.INTERNAL:
            _non_empty(self.internal_statement, "claim.internal_statement")
        elif self.internal_statement is not None:
            raise ReferenceContextError(
                "existing hypothesis and observation content must not be duplicated"
            )
        if self.target_id is not None and not isinstance(self.target_id, TargetId):
            raise ReferenceContextError("claim.target_id must be TargetId")
        if self.scope is not None and not isinstance(self.scope, ClaimScope):
            raise ReferenceContextError("claim.scope must be ClaimScope")


@dataclass(frozen=True, slots=True)
class ReferenceCandidate:
    """An unconfirmed reference candidate, not an EvidenceSource assertion."""

    reference_id: ReferenceId
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.reference_id, ReferenceId):
            raise ReferenceContextError(
                "reference_candidate.reference_id must be ReferenceId"
            )
        if self.reference_id.namespace is not ReferenceNamespace.CANDIDATE:
            raise ReferenceContextError(
                "reference_candidate.reference_id must use candidate namespace"
            )
        _non_empty(self.description, "reference_candidate.description")


@dataclass(frozen=True, slots=True)
class ReferenceSupport:
    """Declare a Reference -> Claim justification-path edge."""

    reference_id: ReferenceId
    claim_id: ClaimId

    def __post_init__(self) -> None:
        if not isinstance(self.reference_id, ReferenceId):
            raise ReferenceContextError("support.reference_id must be ReferenceId")
        if not isinstance(self.claim_id, ClaimId):
            raise ReferenceContextError("support.claim_id must be ClaimId")


@dataclass(frozen=True, slots=True)
class ClaimDependency:
    """Declare an upstream Claim -> dependent Claim derivation-path edge."""

    upstream_claim_id: ClaimId
    dependent_claim_id: ClaimId

    def __post_init__(self) -> None:
        if not isinstance(self.upstream_claim_id, ClaimId):
            raise ReferenceContextError(
                "dependency.upstream_claim_id must be ClaimId"
            )
        if not isinstance(self.dependent_claim_id, ClaimId):
            raise ReferenceContextError(
                "dependency.dependent_claim_id must be ClaimId"
            )


class TemporalRole(StrEnum):
    """The three qualified time roles admitted by W1A."""

    TARGET_EVENT = "target-event"
    CREATION_DERIVATION = "creation-derivation"
    AVAILABLE_TO_CONTEXT = "available-to-context"


class TemporalMarker(StrEnum):
    """Explicit non-instant values, distinct from an absent temporal fact."""

    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


TemporalSubject: TypeAlias = ClaimId | ReferenceId
TemporalValue: TypeAlias = datetime | TemporalMarker


@dataclass(frozen=True, slots=True)
class TemporalFact:
    """One sparse, role-qualified temporal fact about a claim or reference."""

    subject: TemporalSubject
    role: TemporalRole
    value: TemporalValue

    def __post_init__(self) -> None:
        if not isinstance(self.subject, (ClaimId, ReferenceId)):
            raise ReferenceContextError(
                "temporal_fact.subject must be ClaimId or ReferenceId"
            )
        if not isinstance(self.role, TemporalRole):
            raise ReferenceContextError("temporal_fact.role must be TemporalRole")
        if self.role in {
            TemporalRole.TARGET_EVENT,
            TemporalRole.CREATION_DERIVATION,
        } and not isinstance(self.subject, ClaimId):
            raise ReferenceContextError(
                f"{self.role.value} temporal facts require a claim subject"
            )
        if isinstance(self.value, datetime):
            _aware(self.value, "temporal_fact.value")
        elif not isinstance(self.value, TemporalMarker):
            raise ReferenceContextError(
                "temporal_fact.value must be an aware datetime or TemporalMarker"
            )


@dataclass(frozen=True, slots=True)
class AdmissibilityAssertion:
    """Append-only W1A admissibility information, not a lifecycle transition."""

    reference_id: ReferenceId
    admissible: bool
    effective_at: datetime
    known_at: datetime
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(self.reference_id, ReferenceId):
            raise ReferenceContextError(
                "admissibility.reference_id must be ReferenceId"
            )
        if not isinstance(self.admissible, bool):
            raise ReferenceContextError("admissibility.admissible must be boolean")
        _aware(self.effective_at, "admissibility.effective_at")
        _aware(self.known_at, "admissibility.known_at")
        _non_empty(self.rationale, "admissibility.rationale")


class AdmissibilityStatus(StrEnum):
    """Derived W1A view; it carries no presence or sufficiency meaning."""

    ADMISSIBLE = "W1A_ADMISSIBLE"
    INADMISSIBLE = "W1A_INADMISSIBLE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class AgentId:
    """Opaque case-local identity, with no registry, role, or authority meaning."""

    local_id: str

    def __post_init__(self) -> None:
        _non_empty(self.local_id, "agent_id.local_id")


class PresenceStatus(StrEnum):
    """Declared scoped finding, never a computed existence or sufficiency proof."""

    KNOWN_PRESENT = "known_present"
    KNOWN_ABSENT = "known_absent"
    UNRESOLVED = "unresolved"


class AccessStatus(StrEnum):
    """Declared epistemic reachability, not interpretability or control."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class PresenceFinding:
    """Bind a declared presence finding to its existing scope/time/basis claim."""

    reference_id: ReferenceId
    status: PresenceStatus
    claim_id: ClaimId

    def __post_init__(self) -> None:
        if not isinstance(self.reference_id, ReferenceId):
            raise ReferenceContextError("presence.reference_id must be ReferenceId")
        if not isinstance(self.status, PresenceStatus):
            raise ReferenceContextError("presence.status must be PresenceStatus")
        if not isinstance(self.claim_id, ClaimId):
            raise ReferenceContextError("presence.claim_id must be ClaimId")


@dataclass(frozen=True, slots=True)
class AccessFinding:
    """Bind an explicit R/A finding to a claim; infer no access to other R/A."""

    reference_id: ReferenceId
    agent_id: AgentId
    status: AccessStatus
    claim_id: ClaimId

    def __post_init__(self) -> None:
        if not isinstance(self.reference_id, ReferenceId):
            raise ReferenceContextError("access.reference_id must be ReferenceId")
        if not isinstance(self.agent_id, AgentId):
            raise ReferenceContextError("access.agent_id must be AgentId")
        if not isinstance(self.status, AccessStatus):
            raise ReferenceContextError("access.status must be AccessStatus")
        if not isinstance(self.claim_id, ClaimId):
            raise ReferenceContextError("access.claim_id must be ClaimId")


@dataclass(frozen=True, slots=True)
class DirectDependencies:
    """The two direct dependency kinds for one enrolled claim."""

    reference_ids: tuple[ReferenceId, ...]
    claim_ids: tuple[ClaimId, ...]

    def __post_init__(self) -> None:
        _tuple(self.reference_ids, ReferenceId, "dependencies.reference_ids")
        _tuple(self.claim_ids, ClaimId, "dependencies.claim_ids")


@dataclass(frozen=True, slots=True)
class ClaimReferenceRoots:
    """Remaining structural reference roots for one affected claim."""

    claim_id: ClaimId
    reference_ids: tuple[ReferenceId, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.claim_id, ClaimId):
            raise ReferenceContextError("claim_roots.claim_id must be ClaimId")
        _tuple(self.reference_ids, ReferenceId, "claim_roots.reference_ids")


@dataclass(frozen=True, slots=True)
class InvalidationImpact:
    """Structural impact of removing one reference from current support."""

    reference_id: ReferenceId
    direct_claims: tuple[ClaimId, ...]
    transitive_dependents: tuple[ClaimId, ...]
    remaining_roots: tuple[ClaimReferenceRoots, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reference_id, ReferenceId):
            raise ReferenceContextError(
                "invalidation_impact.reference_id must be ReferenceId"
            )
        _tuple(self.direct_claims, ClaimId, "invalidation_impact.direct_claims")
        _tuple(
            self.transitive_dependents,
            ClaimId,
            "invalidation_impact.transitive_dependents",
        )
        _tuple(
            self.remaining_roots,
            ClaimReferenceRoots,
            "invalidation_impact.remaining_roots",
        )

    @property
    def affected_claims(self) -> tuple[ClaimId, ...]:
        return tuple(
            sorted(
                {*self.direct_claims, *self.transitive_dependents},
                key=_claim_sort_key,
            )
        )


def _claim_sort_key(value: ClaimId) -> tuple[str, str]:
    return value.namespace.value, value.local_id


def _reference_sort_key(value: ReferenceId) -> tuple[str, str]:
    return value.namespace.value, value.local_id


@dataclass(frozen=True, slots=True)
class ReferenceContext:
    """Immutable internal overlay over one already validated ``ValidatorInput``."""

    validator_input: ValidatorInput
    claims: tuple[ClaimAnchor, ...] = field(default_factory=tuple)
    reference_candidates: tuple[ReferenceCandidate, ...] = field(
        default_factory=tuple
    )
    reference_supports: tuple[ReferenceSupport, ...] = field(default_factory=tuple)
    claim_dependencies: tuple[ClaimDependency, ...] = field(default_factory=tuple)
    temporal_facts: tuple[TemporalFact, ...] = field(default_factory=tuple)
    admissibility_assertions: tuple[AdmissibilityAssertion, ...] = field(
        default_factory=tuple
    )
    presence_findings: tuple[PresenceFinding, ...] = field(default_factory=tuple)
    access_findings: tuple[AccessFinding, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.validator_input, ValidatorInput):
            raise ReferenceContextError(
                "reference_context.validator_input must be ValidatorInput"
            )
        _tuple(self.claims, ClaimAnchor, "reference_context.claims")
        _tuple(
            self.reference_candidates,
            ReferenceCandidate,
            "reference_context.reference_candidates",
        )
        _tuple(
            self.reference_supports,
            ReferenceSupport,
            "reference_context.reference_supports",
        )
        _tuple(
            self.claim_dependencies,
            ClaimDependency,
            "reference_context.claim_dependencies",
        )
        _tuple(
            self.temporal_facts,
            TemporalFact,
            "reference_context.temporal_facts",
        )
        _tuple(
            self.admissibility_assertions,
            AdmissibilityAssertion,
            "reference_context.admissibility_assertions",
        )
        _tuple(
            self.presence_findings, PresenceFinding,
            "reference_context.presence_findings",
        )
        _tuple(
            self.access_findings, AccessFinding, "reference_context.access_findings"
        )
        self._validate_identities()
        self._validate_relations()
        self._validate_temporal_facts()
        self._validate_admissibility_assertions()
        self._validate_findings()

    def _validate_identities(self) -> None:
        claim_ids = tuple(claim.claim_id for claim in self.claims)
        if len(claim_ids) != len(set(claim_ids)):
            raise ReferenceContextError("claim identifiers must be unique")

        hypothesis_ids = {
            hypothesis.hypothesis_id
            for hypothesis in self.validator_input.hypotheses
        }
        for claim in self.claims:
            if (
                claim.claim_id.namespace is ClaimNamespace.HYPOTHESIS
                and claim.claim_id.local_id not in hypothesis_ids
            ):
                raise ReferenceContextError(
                    "hypothesis claim references an unknown hypothesis_id: "
                    f"{claim.claim_id.local_id!r}"
                )
            if (
                claim.scope is not None
                and claim.scope.source is ScopeSource.REFERENCE_FRAME
                and self.validator_input.reference_frame.scope is None
            ):
                raise ReferenceContextError(
                    "reference-frame claim scope requires ReferenceFrame.scope"
                )

        candidate_ids = tuple(
            candidate.reference_id for candidate in self.reference_candidates
        )
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ReferenceContextError(
                "reference candidate identifiers must be unique"
            )

    def _validate_relations(self) -> None:
        claim_ids = set(self.claim_ids)
        reference_ids = set(self.reference_ids)
        supports = tuple(
            (support.reference_id, support.claim_id)
            for support in self.reference_supports
        )
        if len(supports) != len(set(supports)):
            raise ReferenceContextError("reference support edges must be unique")
        dependencies = tuple(
            (dependency.upstream_claim_id, dependency.dependent_claim_id)
            for dependency in self.claim_dependencies
        )
        if len(dependencies) != len(set(dependencies)):
            raise ReferenceContextError("claim dependency edges must be unique")

        for support in self.reference_supports:
            if support.reference_id not in reference_ids:
                raise ReferenceContextError(
                    f"support references unknown reference {support.reference_id!r}"
                )
            if support.claim_id not in claim_ids:
                raise ReferenceContextError(
                    f"support references unknown claim {support.claim_id!r}"
                )
        for dependency in self.claim_dependencies:
            if dependency.upstream_claim_id not in claim_ids:
                raise ReferenceContextError(
                    "dependency references unknown upstream claim "
                    f"{dependency.upstream_claim_id!r}"
                )
            if dependency.dependent_claim_id not in claim_ids:
                raise ReferenceContextError(
                    "dependency references unknown dependent claim "
                    f"{dependency.dependent_claim_id!r}"
                )

        implicit_supports = set(self._implicit_support_edges())
        duplicate_implicit = set(supports) & implicit_supports
        if duplicate_implicit:
            raise ReferenceContextError(
                "Hypothesis.evidence_source_ids support must not be duplicated"
            )

    def _validate_temporal_facts(self) -> None:
        claim_ids = set(self.claim_ids)
        reference_ids = set(self.reference_ids)
        keys: list[tuple[TemporalSubject, TemporalRole]] = []
        for fact in self.temporal_facts:
            if isinstance(fact.subject, ClaimId):
                if fact.subject not in claim_ids:
                    raise ReferenceContextError(
                        f"temporal fact references unknown claim {fact.subject!r}"
                    )
            elif fact.subject not in reference_ids:
                raise ReferenceContextError(
                    f"temporal fact references unknown reference {fact.subject!r}"
                )
            keys.append((fact.subject, fact.role))
        if len(keys) != len(set(keys)):
            raise ReferenceContextError(
                "each temporal subject and role may have at most one fact"
            )

    def _validate_admissibility_assertions(self) -> None:
        reference_ids = set(self.reference_ids)
        for assertion in self.admissibility_assertions:
            if assertion.reference_id not in reference_ids:
                raise ReferenceContextError(
                    "admissibility assertion references unknown reference "
                    f"{assertion.reference_id!r}"
                )
        if len(self.admissibility_assertions) != len(
            set(self.admissibility_assertions)
        ):
            raise ReferenceContextError(
                "admissibility assertions must not contain exact duplicates"
            )

    def _validate_findings(self) -> None:
        finding_claims: set[ClaimId] = set()
        for finding in (*self.presence_findings, *self.access_findings):
            self._require_reference(finding.reference_id)
            self._require_claim(finding.claim_id)
            if finding.claim_id in finding_claims:
                raise ReferenceContextError(
                    "each finding requires its own claim anchor"
                )
            finding_claims.add(finding.claim_id)
        for finding in self.presence_findings:
            if finding.status is PresenceStatus.UNRESOLVED:
                continue
            if self._claim(finding.claim_id).scope is None:
                raise ReferenceContextError(
                    "determinate presence requires an explicit claim scope"
                )
            if not self._has_presence_basis(finding.claim_id, finding.reference_id):
                raise ReferenceContextError(
                    "determinate presence requires an observation or a declared "
                    "support path beyond the examined reference itself"
                )

    def _has_presence_basis(
        self, claim_id: ClaimId, examined_reference: ReferenceId
    ) -> bool:
        """Check for a structural binding only, never evidence adequacy.

        Observation anchors already reference Observation.provenance.  Other
        paths must reach an observation or a registered supporting reference
        other than the examined R.  Cycles and R's own registration alone do
        not supply this binding.  Neither a successful check nor the source's
        namespace establishes truth, search completeness, or sufficiency.
        """

        visited: set[ClaimId] = set()
        pending = [claim_id]
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            if current.namespace is ClaimNamespace.OBSERVATION:
                return True
            dependencies = self.direct_dependencies(current)
            if any(r != examined_reference for r in dependencies.reference_ids):
                return True
            pending.extend(dependencies.claim_ids)
        return False

    @property
    def claim_ids(self) -> tuple[ClaimId, ...]:
        """Return only explicitly enrolled claims, in deterministic order."""

        return tuple(
            sorted((claim.claim_id for claim in self.claims), key=_claim_sort_key)
        )

    @property
    def reference_ids(self) -> tuple[ReferenceId, ...]:
        """Return input sources and candidates without equating their status."""

        evidence_ids = (
            ReferenceId.evidence_source(source.source_id)
            for source in self.validator_input.calibration.evidence_sources
        )
        candidate_ids = (
            candidate.reference_id for candidate in self.reference_candidates
        )
        return tuple(
            sorted((*evidence_ids, *candidate_ids), key=_reference_sort_key)
        )

    def _require_claim(self, claim_id: ClaimId) -> None:
        if not isinstance(claim_id, ClaimId) or claim_id not in set(self.claim_ids):
            raise ReferenceContextError(f"unknown claim {claim_id!r}")

    def _require_reference(self, reference_id: ReferenceId) -> None:
        if (
            not isinstance(reference_id, ReferenceId)
            or reference_id not in set(self.reference_ids)
        ):
            raise ReferenceContextError(f"unknown reference {reference_id!r}")

    def _claim(self, claim_id: ClaimId) -> ClaimAnchor:
        self._require_claim(claim_id)
        return next(claim for claim in self.claims if claim.claim_id == claim_id)

    def claim_content(self, claim_id: ClaimId) -> str:
        """Resolve claim content from its anchor without copying public content."""

        claim = self._claim(claim_id)
        if claim_id.namespace is ClaimNamespace.HYPOTHESIS:
            return next(
                hypothesis.statement
                for hypothesis in self.validator_input.hypotheses
                if hypothesis.hypothesis_id == claim_id.local_id
            )
        if claim_id.namespace is ClaimNamespace.OBSERVATION:
            return self.validator_input.observation.content
        assert claim.internal_statement is not None
        return claim.internal_statement

    def reference_description(self, reference_id: ReferenceId) -> str:
        """Resolve source or candidate text while retaining namespace semantics."""

        self._require_reference(reference_id)
        if reference_id.namespace is ReferenceNamespace.EVIDENCE_SOURCE:
            return next(
                source.description
                for source in self.validator_input.calibration.evidence_sources
                if source.source_id == reference_id.local_id
            )
        return next(
            candidate.description
            for candidate in self.reference_candidates
            if candidate.reference_id == reference_id
        )

    def scope_text(self, claim_id: ClaimId) -> str | None:
        """Resolve an explicit scope; ``None`` means no scope was modeled."""

        scope = self._claim(claim_id).scope
        if scope is None:
            return None
        if scope.source is ScopeSource.REFERENCE_FRAME:
            return self.validator_input.reference_frame.scope
        return scope.text

    def _implicit_support_edges(self) -> tuple[tuple[ReferenceId, ClaimId], ...]:
        enrolled_hypotheses = {
            claim_id.local_id
            for claim_id in self.claim_ids
            if claim_id.namespace is ClaimNamespace.HYPOTHESIS
        }
        edges = {
            (
                ReferenceId.evidence_source(source_id),
                ClaimId.hypothesis(hypothesis.hypothesis_id),
            )
            for hypothesis in self.validator_input.hypotheses
            if hypothesis.hypothesis_id in enrolled_hypotheses
            for source_id in hypothesis.evidence_source_ids
        }
        return tuple(
            sorted(
                edges,
                key=lambda edge: (
                    _reference_sort_key(edge[0]),
                    _claim_sort_key(edge[1]),
                ),
            )
        )

    def _all_support_edges(self) -> tuple[tuple[ReferenceId, ClaimId], ...]:
        explicit = {
            (support.reference_id, support.claim_id)
            for support in self.reference_supports
        }
        edges = {*self._implicit_support_edges(), *explicit}
        return tuple(
            sorted(
                edges,
                key=lambda edge: (
                    _reference_sort_key(edge[0]),
                    _claim_sort_key(edge[1]),
                ),
            )
        )

    def direct_dependencies(self, claim_id: ClaimId) -> DirectDependencies:
        """Return direct reference support and upstream claim dependencies."""

        self._require_claim(claim_id)
        references = {
            reference_id
            for reference_id, supported_claim_id in self._all_support_edges()
            if supported_claim_id == claim_id
        }
        claims = {
            dependency.upstream_claim_id
            for dependency in self.claim_dependencies
            if dependency.dependent_claim_id == claim_id
        }
        return DirectDependencies(
            reference_ids=tuple(sorted(references, key=_reference_sort_key)),
            claim_ids=tuple(sorted(claims, key=_claim_sort_key)),
        )

    def _direct_dependent_claims(
        self, subject: ClaimId | ReferenceId
    ) -> set[ClaimId]:
        if isinstance(subject, ReferenceId):
            return {
                claim_id
                for reference_id, claim_id in self._all_support_edges()
                if reference_id == subject
            }
        return {
            dependency.dependent_claim_id
            for dependency in self.claim_dependencies
            if dependency.upstream_claim_id == subject
        }

    def transitive_dependents(
        self, subject: ClaimId | ReferenceId
    ) -> tuple[ClaimId, ...]:
        """Return the cycle-safe, non-reflexive dependent closure."""

        if isinstance(subject, ClaimId):
            self._require_claim(subject)
            excluded = subject
        elif isinstance(subject, ReferenceId):
            self._require_reference(subject)
            excluded = None
        else:
            raise ReferenceContextError("subject must be ClaimId or ReferenceId")

        result: set[ClaimId] = set()
        pending = list(self._direct_dependent_claims(subject))
        while pending:
            claim_id = pending.pop()
            if claim_id == excluded or claim_id in result:
                continue
            result.add(claim_id)
            pending.extend(self._direct_dependent_claims(claim_id))
        return tuple(sorted(result, key=_claim_sort_key))

    def reference_roots(self, claim_id: ClaimId) -> tuple[ReferenceId, ...]:
        """Return unique structural roots without asserting independence."""

        self._require_claim(claim_id)
        roots: set[ReferenceId] = set()
        visited: set[ClaimId] = set()
        pending = [claim_id]
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            direct = self.direct_dependencies(current)
            roots.update(direct.reference_ids)
            pending.extend(direct.claim_ids)
        return tuple(sorted(roots, key=_reference_sort_key))

    def temporal_value(
        self,
        subject: TemporalSubject,
        role: TemporalRole,
    ) -> TemporalValue | None:
        """Return a modeled value; ``None`` remains distinct from both markers."""

        if isinstance(subject, ClaimId):
            self._require_claim(subject)
        elif isinstance(subject, ReferenceId):
            self._require_reference(subject)
        else:
            raise ReferenceContextError("subject must be ClaimId or ReferenceId")
        if not isinstance(role, TemporalRole):
            raise ReferenceContextError("role must be TemporalRole")
        return next(
            (
                fact.value
                for fact in self.temporal_facts
                if fact.subject == subject and fact.role is role
            ),
            None,
        )

    def availability_at(
        self,
        subject: TemporalSubject,
        at: datetime,
    ) -> bool | TemporalMarker | None:
        """Resolve only explicit W1A context availability at one cutoff."""

        _aware(at, "availability.at")
        value = self.temporal_value(subject, TemporalRole.AVAILABLE_TO_CONTEXT)
        if isinstance(value, datetime):
            return value <= at
        return value

    def available_reference_roots(
        self,
        claim_id: ClaimId,
        at: datetime,
    ) -> tuple[ReferenceId, ...]:
        """Return roots on paths explicitly available by a historical cutoff.

        Every upstream claim and root on a qualifying path must have a known
        available-to-context instant no later than ``at``.  Neither temporal
        marker nor an unmodeled fact authorizes inclusion in this historical
        view.
        """

        self._require_claim(claim_id)
        _aware(at, "available_reference_roots.at")

        def is_available(subject: TemporalSubject) -> bool:
            return self.availability_at(subject, at) is True

        def walk(current: ClaimId, path: frozenset[ClaimId]) -> set[ReferenceId]:
            if current in path:
                return set()
            roots: set[ReferenceId] = set()
            dependencies = self.direct_dependencies(current)
            roots.update(
                reference_id
                for reference_id in dependencies.reference_ids
                if is_available(reference_id)
            )
            next_path = path | {current}
            for upstream_claim_id in dependencies.claim_ids:
                if is_available(upstream_claim_id):
                    roots.update(walk(upstream_claim_id, next_path))
            return roots

        return tuple(sorted(walk(claim_id, frozenset()), key=_reference_sort_key))

    def admissibility_at(
        self,
        reference_id: ReferenceId,
        *,
        effective_at: datetime,
        known_at: datetime,
    ) -> AdmissibilityStatus:
        """Derive an order-independent admissibility view for two time axes."""

        self._require_reference(reference_id)
        _aware(effective_at, "admissibility_view.effective_at")
        _aware(known_at, "admissibility_view.known_at")
        applicable = tuple(
            assertion
            for assertion in self.admissibility_assertions
            if assertion.reference_id == reference_id
            and assertion.effective_at <= effective_at
            and assertion.known_at <= known_at
        )
        if not applicable:
            return AdmissibilityStatus.UNRESOLVED

        latest_key = max(
            (assertion.effective_at, assertion.known_at)
            for assertion in applicable
        )
        latest_values = {
            assertion.admissible
            for assertion in applicable
            if (assertion.effective_at, assertion.known_at) == latest_key
        }
        if len(latest_values) != 1:
            return AdmissibilityStatus.UNRESOLVED
        return (
            AdmissibilityStatus.ADMISSIBLE
            if latest_values.pop()
            else AdmissibilityStatus.INADMISSIBLE
        )

    def current_admissibility(
        self,
        reference_id: ReferenceId,
        at: datetime,
    ) -> AdmissibilityStatus:
        """Use the same instant as effective and epistemic cutoff."""

        return self.admissibility_at(
            reference_id,
            effective_at=at,
            known_at=at,
        )

    def presence_findings_for(
        self, reference_id: ReferenceId
    ) -> tuple[PresenceFinding, ...]:
        """Return every stored finding for R, including undated/conflicting ones."""

        self._require_reference(reference_id)
        return tuple(
            sorted(
                (f for f in self.presence_findings if f.reference_id == reference_id),
                key=lambda f: _claim_sort_key(f.claim_id),
            )
        )

    def access_findings_for(
        self, reference_id: ReferenceId, agent_id: AgentId
    ) -> tuple[AccessFinding, ...]:
        """Return all stored findings for exactly R/A, without path inference."""

        self._require_reference(reference_id)
        if not isinstance(agent_id, AgentId):
            raise ReferenceContextError("access query requires AgentId")
        return tuple(
            sorted(
                (
                    f for f in self.access_findings
                    if f.reference_id == reference_id and f.agent_id == agent_id
                ),
                key=lambda f: _claim_sort_key(f.claim_id),
            )
        )

    def _finding_matches_time(
        self, claim_id: ClaimId, target_time: datetime, knowledge_cutoff: datetime
    ) -> bool:
        """Use the finding's own event and knowledge times, never root times.

        Missing/non-instant facts cannot authorize a dated view.  Creation
        time is not knowledge time, and an event instant is not a valid-from
        boundary.  The view records declared findings; it does not re-evaluate
        their justification paths or admissibility.
        """

        event = self.temporal_value(claim_id, TemporalRole.TARGET_EVENT)
        known = self.temporal_value(claim_id, TemporalRole.AVAILABLE_TO_CONTEXT)
        # Compare instants, including distinct folds of the same local time.
        return (
            isinstance(event, datetime)
            and isinstance(known, datetime)
            and _instant_key(event) == _instant_key(target_time)
            and _instant_key(known) <= _instant_key(knowledge_cutoff)
        )

    def presence_findings_at(
        self,
        reference_id: ReferenceId,
        *,
        scope: ClaimScope,
        target_time: datetime,
        knowledge_cutoff: datetime,
    ) -> tuple[PresenceFinding, ...]:
        """Retain all findings matching the exact scope/event and known cutoff.

        Scope equality is explicit declaration equality, not inferred semantic
        equivalence or inclusion.  No fallback to ReferenceFrame.scope occurs.
        """

        if not isinstance(scope, ClaimScope):
            raise ReferenceContextError("presence query requires an explicit scope")
        if (
            scope.source is ScopeSource.REFERENCE_FRAME
            and self.validator_input.reference_frame.scope is None
        ):
            raise ReferenceContextError("reference-frame scope is not modeled")
        _aware(target_time, "presence.target_time")
        _aware(knowledge_cutoff, "presence.knowledge_cutoff")
        return tuple(
            finding for finding in self.presence_findings_for(reference_id)
            if self._claim(finding.claim_id).scope == scope
            and self._finding_matches_time(
                finding.claim_id, target_time, knowledge_cutoff
            )
        )

    def access_findings_at(
        self,
        reference_id: ReferenceId,
        agent_id: AgentId,
        *,
        target_time: datetime,
        knowledge_cutoff: datetime,
    ) -> tuple[AccessFinding, ...]:
        """Retain all findings for exactly R/A/event known by the given cutoff."""

        _aware(target_time, "access.target_time")
        _aware(knowledge_cutoff, "access.knowledge_cutoff")
        return tuple(
            finding for finding in self.access_findings_for(reference_id, agent_id)
            if self._finding_matches_time(
                finding.claim_id, target_time, knowledge_cutoff
            )
        )

    def presence_at(
        self,
        reference_id: ReferenceId,
        *,
        scope: ClaimScope,
        target_time: datetime,
        knowledge_cutoff: datetime,
    ) -> PresenceStatus:
        """Summarize matching declarations; never overwrite or rank findings.

        Empty, explicitly unresolved, and conflicting views all summarize to
        unresolved.  presence_findings_at retains their distinct underlying
        records.  More findings and later arrivals have no deciding vote.
        """

        statuses = {
            finding.status
            for finding in self.presence_findings_at(
                reference_id, scope=scope, target_time=target_time,
                knowledge_cutoff=knowledge_cutoff,
            )
        }
        if len(statuses) == 1:
            return next(iter(statuses))
        return PresenceStatus.UNRESOLVED

    def access_at(
        self,
        reference_id: ReferenceId,
        agent_id: AgentId,
        *,
        target_time: datetime,
        knowledge_cutoff: datetime,
    ) -> AccessStatus:
        """Summarize access declarations, without interpreting their contents.

        Conflicting content claims need not mean conflicting access findings.
        access_findings_at preserves all matching records, even when the
        summary is unresolved.  Neither time of arrival nor count breaks ties.
        """

        statuses = {
            finding.status
            for finding in self.access_findings_at(
                reference_id, agent_id, target_time=target_time,
                knowledge_cutoff=knowledge_cutoff,
            )
        }
        if len(statuses) == 1:
            return next(iter(statuses))
        return AccessStatus.UNRESOLVED

    def invalidation_impact(
        self, reference_id: ReferenceId
    ) -> InvalidationImpact:
        """Trace structural impact without mutating claims or judging support."""

        self._require_reference(reference_id)
        direct_claims = tuple(
            sorted(
                self._direct_dependent_claims(reference_id),
                key=_claim_sort_key,
            )
        )
        affected = set(direct_claims)
        for direct_claim_id in direct_claims:
            affected.update(self.transitive_dependents(direct_claim_id))
        transitive = tuple(
            sorted(affected - set(direct_claims), key=_claim_sort_key)
        )
        remaining_roots = tuple(
            ClaimReferenceRoots(
                claim_id=claim_id,
                reference_ids=tuple(
                    root
                    for root in self.reference_roots(claim_id)
                    if root != reference_id
                ),
            )
            for claim_id in sorted(affected, key=_claim_sort_key)
        )
        return InvalidationImpact(
            reference_id=reference_id,
            direct_claims=direct_claims,
            transitive_dependents=transitive,
            remaining_roots=remaining_roots,
        )
