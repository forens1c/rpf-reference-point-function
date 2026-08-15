# Copyright 2026 Björn (frenetik.B)
# SPDX-License-Identifier: Apache-2.0

"""Immutable models for non-authoritative reference-frame proposals.

The contract in this module deliberately stops before validator input
construction.  A classification provider may describe candidate reference
frames and their provenance, but it cannot set RPF process status, reason
codes, transitions, competence, evidence strength, or actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from math import isfinite
from numbers import Real
import re
from typing import Final

from rpf_validator.enums import ReferenceFrameClass, ReferenceFrameStatus
from rpf_validator.errors import InputValidationError

CLASSIFICATION_PROPOSAL_SCHEMA_VERSION: Final = (
    "rpf-classification-proposal-0.1"
)
PROVIDER_CONFIDENCE_SCALE_ID: Final = "provider-self-report-unit-interval-0.1"
MAX_EVIDENCE_EXCERPT_LENGTH: Final = 500

_SHA256_HEX = re.compile(r"[0-9a-f]{64}\Z")
_RFC3339_DATE_TIME = re.compile(
    r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})\Z"
)


class ProposalRole(StrEnum):
    """The only authority role available to a provider output."""

    NON_AUTHORITATIVE_SUGGESTION = "NON_AUTHORITATIVE_SUGGESTION"


class ProviderKind(StrEnum):
    """Implementation families supported by the first proposal contract."""

    RULE_BASED = "RULE_BASED"
    MODEL_BASED = "MODEL_BASED"


class DigestAlgorithm(StrEnum):
    """Digest algorithms admitted by contract 0.1."""

    SHA_256 = "sha-256"


class DigestCanonicalization(StrEnum):
    """Byte representations that may be bound by a digest."""

    RAW_UTF8 = "raw-utf8"
    RFC8785_JSON = "rfc8785-json"


def _non_empty(value: object, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InputValidationError(path, "must be a non-empty string")


def _optional_non_empty(value: object, path: str) -> None:
    if value is not None:
        _non_empty(value, path)


def _enum(value: object, expected: type[object], path: str) -> None:
    if not isinstance(value, expected):
        raise InputValidationError(path, f"must be {expected.__name__}")


def _tuple(value: object, item_type: type[object], path: str) -> None:
    if not isinstance(value, tuple):
        raise InputValidationError(path, "must be a tuple")
    for index, item in enumerate(value):
        if not isinstance(item, item_type):
            raise InputValidationError(
                f"{path}[{index}]", f"must be {item_type.__name__}"
            )


def _string_tuple(value: object, path: str) -> None:
    _tuple(value, str, path)
    for index, item in enumerate(value):
        _non_empty(item, f"{path}[{index}]")


def _unique(values: tuple[str, ...], path: str) -> None:
    if len(values) != len(set(values)):
        raise InputValidationError(path, "must contain unique identifiers")


def _unit_interval(value: object, path: str, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputValidationError(path, "must be a number from 0.0 to 1.0")
    numeric = float(value)
    if not isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise InputValidationError(path, "must be between 0.0 and 1.0")


def _non_negative_int(value: object, path: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InputValidationError(path, "must be a non-negative integer")


def _positive_int(value: object, path: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise InputValidationError(path, "must be a positive integer")


def _rfc3339(value: object, path: str) -> None:
    _non_empty(value, path)
    assert isinstance(value, str)
    if not _RFC3339_DATE_TIME.fullmatch(value):
        raise InputValidationError(path, "must be an RFC 3339 date-time")
    candidate = value[:-1] + "+00:00" if value[-1] in "Zz" else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise InputValidationError(path, "must be an RFC 3339 date-time") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InputValidationError(path, "must include an explicit UTC offset")


@dataclass(frozen=True, slots=True)
class ContentDigest:
    """A digest plus the exact byte representation it binds."""

    algorithm: DigestAlgorithm
    canonicalization: DigestCanonicalization
    value: str

    def __post_init__(self) -> None:
        _enum(self.algorithm, DigestAlgorithm, "digest.algorithm")
        _enum(
            self.canonicalization,
            DigestCanonicalization,
            "digest.canonicalization",
        )
        if not isinstance(self.value, str) or not _SHA256_HEX.fullmatch(self.value):
            raise InputValidationError(
                "digest.value", "must be 64 lowercase hexadecimal characters"
            )


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    """Stable provider identity without any self-assigned authority level."""

    provider_id: str
    provider_version: str
    provider_kind: ProviderKind
    configuration_digest: ContentDigest
    model_id: str | None = None
    model_version: str | None = None

    def __post_init__(self) -> None:
        _non_empty(self.provider_id, "provider.provider_id")
        _non_empty(self.provider_version, "provider.provider_version")
        _enum(self.provider_kind, ProviderKind, "provider.provider_kind")
        if not isinstance(self.configuration_digest, ContentDigest):
            raise InputValidationError(
                "provider.configuration_digest", "must be ContentDigest"
            )
        _optional_non_empty(self.model_id, "provider.model_id")
        _optional_non_empty(self.model_version, "provider.model_version")
        model_fields = (self.model_id, self.model_version)
        if self.provider_kind is ProviderKind.MODEL_BASED:
            if any(item is None for item in model_fields):
                raise InputValidationError(
                    "provider",
                    "MODEL_BASED requires model_id and model_version",
                )
        elif any(item is not None for item in model_fields):
            raise InputValidationError(
                "provider",
                "RULE_BASED must not declare model_id or model_version",
            )


@dataclass(frozen=True, slots=True)
class ProposalInputReference:
    """Binding to the case, subject, and exact text supplied to a provider."""

    case_id: str
    assessment_subject_id: str
    source_id: str
    media_type: str
    payload_digest: ContentDigest

    def __post_init__(self) -> None:
        _non_empty(self.case_id, "input_reference.case_id")
        _non_empty(
            self.assessment_subject_id,
            "input_reference.assessment_subject_id",
        )
        _non_empty(self.source_id, "input_reference.source_id")
        _non_empty(self.media_type, "input_reference.media_type")
        if not self.media_type.lower().startswith("text/"):
            raise InputValidationError(
                "input_reference.media_type", "must identify textual content"
            )
        if not isinstance(self.payload_digest, ContentDigest):
            raise InputValidationError(
                "input_reference.payload_digest", "must be ContentDigest"
            )
        if (
            self.payload_digest.canonicalization
            is not DigestCanonicalization.RAW_UTF8
        ):
            raise InputValidationError(
                "input_reference.payload_digest.canonicalization",
                "must be raw-utf8 in contract 0.1",
            )


@dataclass(frozen=True, slots=True)
class EvidenceFragment:
    """A byte-addressed source fragment used to ground a candidate."""

    evidence_id: str
    source_id: str
    start_byte: int
    end_byte: int
    fragment_digest: ContentDigest
    excerpt: str | None = None

    def __post_init__(self) -> None:
        _non_empty(self.evidence_id, "evidence_fragment.evidence_id")
        _non_empty(self.source_id, "evidence_fragment.source_id")
        _non_negative_int(self.start_byte, "evidence_fragment.start_byte")
        _positive_int(self.end_byte, "evidence_fragment.end_byte")
        if self.end_byte <= self.start_byte:
            raise InputValidationError(
                "evidence_fragment.end_byte", "must be greater than start_byte"
            )
        if not isinstance(self.fragment_digest, ContentDigest):
            raise InputValidationError(
                "evidence_fragment.fragment_digest", "must be ContentDigest"
            )
        if (
            self.fragment_digest.canonicalization
            is not DigestCanonicalization.RAW_UTF8
        ):
            raise InputValidationError(
                "evidence_fragment.fragment_digest.canonicalization",
                "must be raw-utf8 in contract 0.1",
            )
        _optional_non_empty(self.excerpt, "evidence_fragment.excerpt")
        if (
            self.excerpt is not None
            and len(self.excerpt) > MAX_EVIDENCE_EXCERPT_LENGTH
        ):
            raise InputValidationError(
                "evidence_fragment.excerpt",
                f"must not exceed {MAX_EVIDENCE_EXCERPT_LENGTH} characters",
            )


@dataclass(frozen=True, slots=True)
class FrameCandidate:
    """One non-authoritative reference-frame classification candidate."""

    candidate_id: str
    status: ReferenceFrameStatus
    classes: tuple[ReferenceFrameClass, ...]
    scope: str | None
    rationale: str
    provider_confidence: float | None
    provider_confidence_rationale: str
    confidence_scale_id: str = PROVIDER_CONFIDENCE_SCALE_ID
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _non_empty(self.candidate_id, "candidate.candidate_id")
        _enum(self.status, ReferenceFrameStatus, "candidate.status")
        _tuple(self.classes, ReferenceFrameClass, "candidate.classes")
        if len(self.classes) != len(set(self.classes)):
            raise InputValidationError(
                "candidate.classes", "must not contain duplicates"
            )
        _optional_non_empty(self.scope, "candidate.scope")
        _non_empty(self.rationale, "candidate.rationale")
        _unit_interval(
            self.provider_confidence,
            "candidate.provider_confidence",
            optional=True,
        )
        _non_empty(
            self.provider_confidence_rationale,
            "candidate.provider_confidence_rationale",
        )
        _non_empty(self.confidence_scale_id, "candidate.confidence_scale_id")
        if self.confidence_scale_id != PROVIDER_CONFIDENCE_SCALE_ID:
            raise InputValidationError(
                "candidate.confidence_scale_id",
                f"must equal {PROVIDER_CONFIDENCE_SCALE_ID!r}",
            )
        _string_tuple(self.evidence_ids, "candidate.evidence_ids")
        _unique(self.evidence_ids, "candidate.evidence_ids")
        _string_tuple(self.assumptions, "candidate.assumptions")
        _unique(self.assumptions, "candidate.assumptions")

        if self.status is ReferenceFrameStatus.MISSING:
            if self.classes:
                raise InputValidationError(
                    "candidate.classes", "must be empty when status is MISSING"
                )
            if self.scope is not None:
                raise InputValidationError(
                    "candidate.scope", "must be null when status is MISSING"
                )
        else:
            if not self.classes:
                raise InputValidationError(
                    "candidate.classes",
                    "must contain at least one class when a frame is proposed",
                )
            if self.scope is None:
                raise InputValidationError(
                    "candidate.scope",
                    "must be present when status is IDENTIFIED or AMBIGUOUS",
                )


@dataclass(frozen=True, slots=True)
class ProposalUncertainty:
    """A structured uncertainty item without an aggregate risk score."""

    uncertainty_id: str
    description: str
    affects_candidate_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _non_empty(self.uncertainty_id, "uncertainty.uncertainty_id")
        _non_empty(self.description, "uncertainty.description")
        _string_tuple(
            self.affects_candidate_ids,
            "uncertainty.affects_candidate_ids",
        )
        if not self.affects_candidate_ids:
            raise InputValidationError(
                "uncertainty.affects_candidate_ids",
                "must identify at least one affected candidate",
            )
        _unique(
            self.affects_candidate_ids,
            "uncertainty.affects_candidate_ids",
        )


@dataclass(frozen=True, slots=True)
class ClassificationProposal:
    """Versioned provider output that cannot directly decide an RPF result."""

    schema_version: str
    proposal_id: str
    proposal_role: ProposalRole
    provider: ProviderMetadata
    input_reference: ProposalInputReference
    preferred_candidate_id: str
    candidates: tuple[FrameCandidate, ...]
    evidence_fragments: tuple[EvidenceFragment, ...] = field(default_factory=tuple)
    uncertainties: tuple[ProposalUncertainty, ...] = field(default_factory=tuple)
    generated_at: str | None = None

    def __post_init__(self) -> None:
        if self.schema_version != CLASSIFICATION_PROPOSAL_SCHEMA_VERSION:
            raise InputValidationError(
                "classification_proposal.schema_version",
                f"must equal {CLASSIFICATION_PROPOSAL_SCHEMA_VERSION!r}",
            )
        _non_empty(self.proposal_id, "classification_proposal.proposal_id")
        _enum(
            self.proposal_role,
            ProposalRole,
            "classification_proposal.proposal_role",
        )
        if self.proposal_role is not ProposalRole.NON_AUTHORITATIVE_SUGGESTION:
            raise InputValidationError(
                "classification_proposal.proposal_role",
                "must remain NON_AUTHORITATIVE_SUGGESTION",
            )
        if not isinstance(self.provider, ProviderMetadata):
            raise InputValidationError(
                "classification_proposal.provider", "must be ProviderMetadata"
            )
        if not isinstance(self.input_reference, ProposalInputReference):
            raise InputValidationError(
                "classification_proposal.input_reference",
                "must be ProposalInputReference",
            )
        _non_empty(
            self.preferred_candidate_id,
            "classification_proposal.preferred_candidate_id",
        )
        _tuple(
            self.candidates,
            FrameCandidate,
            "classification_proposal.candidates",
        )
        if not self.candidates:
            raise InputValidationError(
                "classification_proposal.candidates",
                "must contain at least one candidate",
            )
        _tuple(
            self.evidence_fragments,
            EvidenceFragment,
            "classification_proposal.evidence_fragments",
        )
        _tuple(
            self.uncertainties,
            ProposalUncertainty,
            "classification_proposal.uncertainties",
        )
        if self.generated_at is not None:
            _rfc3339(self.generated_at, "classification_proposal.generated_at")

        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        evidence_ids = tuple(item.evidence_id for item in self.evidence_fragments)
        uncertainty_ids = tuple(item.uncertainty_id for item in self.uncertainties)
        _unique(candidate_ids, "classification_proposal.candidates")
        _unique(evidence_ids, "classification_proposal.evidence_fragments")
        _unique(uncertainty_ids, "classification_proposal.uncertainties")

        candidate_id_set = set(candidate_ids)
        evidence_id_set = set(evidence_ids)
        if self.preferred_candidate_id not in candidate_id_set:
            raise InputValidationError(
                "classification_proposal.preferred_candidate_id",
                "must reference a declared candidate",
            )
        for candidate in self.candidates:
            unknown = sorted(set(candidate.evidence_ids) - evidence_id_set)
            if unknown:
                raise InputValidationError(
                    f"classification_proposal.candidates[{candidate.candidate_id}]"
                    ".evidence_ids",
                    "references unknown evidence: " + ", ".join(unknown),
                )
        for fragment in self.evidence_fragments:
            if fragment.source_id != self.input_reference.source_id:
                raise InputValidationError(
                    "classification_proposal.evidence_fragments"
                    f"[{fragment.evidence_id}]"
                    ".source_id",
                    "must match input_reference.source_id",
                )
        for uncertainty in self.uncertainties:
            unknown = sorted(
                set(uncertainty.affects_candidate_ids) - candidate_id_set
            )
            if unknown:
                raise InputValidationError(
                    "classification_proposal.uncertainties"
                    f"[{uncertainty.uncertainty_id}].affects_candidate_ids",
                    "references unknown candidates: " + ", ".join(unknown),
                )


def verify_source_payload(proposal: ClassificationProposal, payload: str) -> None:
    """Verify the source digest and every declared byte-addressed fragment.

    This is integrity checking only.  A matching digest does not establish the
    truth, independence, quality, or authority of the supplied content.
    """

    if not isinstance(proposal, ClassificationProposal):
        raise InputValidationError(
            "classification_proposal",
            "must be ClassificationProposal",
        )
    if not isinstance(payload, str):
        raise InputValidationError("source_payload", "must be a string")

    payload_bytes = payload.encode("utf-8")
    actual = sha256(payload_bytes).hexdigest()
    expected = proposal.input_reference.payload_digest.value
    if actual != expected:
        raise InputValidationError(
            "classification_proposal.input_reference.payload_digest.value",
            "does not match the supplied UTF-8 source payload",
        )

    for fragment in proposal.evidence_fragments:
        path = (
            "classification_proposal.evidence_fragments"
            f"[{fragment.evidence_id}]"
        )
        if fragment.end_byte > len(payload_bytes):
            raise InputValidationError(
                f"{path}.end_byte", "exceeds the supplied source payload"
            )
        fragment_bytes = payload_bytes[fragment.start_byte : fragment.end_byte]
        actual_fragment = sha256(fragment_bytes).hexdigest()
        if actual_fragment != fragment.fragment_digest.value:
            raise InputValidationError(
                f"{path}.fragment_digest.value",
                "does not match the declared source byte range",
            )
        if fragment.excerpt is not None:
            try:
                decoded = fragment_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise InputValidationError(
                    f"{path}.excerpt",
                    "byte range does not align to UTF-8 text boundaries",
                ) from exc
            if decoded != fragment.excerpt:
                raise InputValidationError(
                    f"{path}.excerpt",
                    "does not match the declared source byte range",
                )
