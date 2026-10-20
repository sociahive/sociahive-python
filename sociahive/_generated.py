# AUTO-GENERATED from SociaHive's public v1 OpenAPI spec (https://www.sociahive.com/api/v1/openapi.json). Do not edit by hand.
# Every field is optional here (total=False); the API reference says which are always present.
# Platform ids are typed as str: new platforms arrive as plain strings.
from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict, Union


class Error(TypedDict, total=False):
    error: str
    error_description: str


class ConnectedAccount(TypedDict, total=False):
    id: str
    platform: str
    platform_user_id: str
    platform_username: str
    display_name: str
    is_active: bool
    created_at: str
    text_limit: int


class PostAutomationDTO(TypedDict, total=False):
    state: str
    flow_id: str
    flow_name: str
    door: str
    account_id: str
    armed: bool
    bound: bool
    error: Dict[str, Any]
    allowed_actions: List[str]
    flow_live_waiting_for_post: bool


class Post(TypedDict, total=False):
    id: str
    content: Dict[str, Any]
    text: str
    media: List[Dict[str, Any]]
    status: Literal["draft", "scheduled", "publishing", "published", "partially_published", "failed", "pending_approval", "reminder_sent"]
    platforms: List[Dict[str, Any]]
    scheduled_at: str
    timezone: str
    created_at: str
    updated_at: str
    automation: "PostAutomationDTO"
    source: str


class Contact(TypedDict, total=False):
    _id: str
    owner_user_id: str
    platform_identities: List[Dict[str, Any]]
    display_name: str
    email: str
    phone: str
    avatar_url: str
    status: str
    source: str
    tags: List[str]
    notes: str
    interaction_count: float
    first_interaction_at: str
    last_active_at: str
    created_at: str
    updated_at: str


class PaginatedPosts(TypedDict, total=False):
    data: List["Post"]
    pagination: Dict[str, Any]


class PostEnvelope(TypedDict, total=False):
    """Single-post envelope — `{ data: <post> }`."""
    data: "Post"


class ContactEnvelope(TypedDict, total=False):
    """Single-contact envelope — `{ data: <contact> }`."""
    data: "Contact"


class ObjectEnvelope(TypedDict, total=False):
    """Generic `{ data: <object> }` envelope."""
    data: Dict[str, Any]


class BulkOperationResult(TypedDict, total=False):
    total: float
    succeeded: float
    failed: float
    errors: List[Dict[str, Any]]


class BulkOperationResultEnvelope(TypedDict, total=False):
    data: "BulkOperationResult"


class CalendarMonthEnvelope(TypedDict, total=False):
    data: Dict[str, Any]


class ContactListEnvelope(TypedDict, total=False):
    """GET /contacts wraps the paged RESULT OBJECT in `data` — not a bare array."""
    data: Dict[str, Any]


class FlowScheduledPostChip(TypedDict, total=False):
    id: str
    scheduled_at: Union[str, None]
    status: str
    thumbnail_url: Union[str, None]


class FlowListEnvelope(TypedDict, total=False):
    """GET /flows returns `{ flows: [...] }` — raw flow documents decorated with total_triggers / unique_users / unique_clickers, and `scheduled_post` on a flow that belongs to a scheduled post (when post automations are on). Not paginated."""
    flows: List[Dict[str, Any]]


class FlowEnvelope(TypedDict, total=False):
    """POST /flows returns `{ flow: <raw flow document> }` with HTTP 200."""
    flow: Dict[str, Any]


class FlowGraphEnvelope(TypedDict, total=False):
    flow: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class FlowUpdateEnvelope(TypedDict, total=False):
    """PATCH /flows/{id} returns `{ success, flow }`; `warnings` (keyword conflicts) only when non-empty."""
    success: bool
    flow: Dict[str, Any]
    warnings: List[Dict[str, Any]]


class FlowNodeEnvelope(TypedDict, total=False):
    node: Dict[str, Any]


class FlowEdgeEnvelope(TypedDict, total=False):
    edge: Dict[str, Any]


class FlowStats(TypedDict, total=False):
    """Bare (un-enveloped) body returned by GET /flows/{id}/stats."""
    total_triggers: float
    total_button_clicks: float
    unique_users: float
    status_breakdown: Dict[str, Any]
    daily_timeline: List[Dict[str, Any]]


class CollectedDataPage(TypedDict, total=False):
    success: bool
    data: List[Dict[str, Any]]
    pagination: Dict[str, Any]
    filters: Dict[str, Any]


class CreatePostRequest(TypedDict, total=False):
    content: Dict[str, Any]
    platform_overrides: Dict[str, Dict[str, Any]]
    platforms: List[Dict[str, Any]]
    schedule_type: Literal["immediate", "scheduled"]
    scheduled_at: str
    timezone: str


class PostImportResult(TypedDict, total=False):
    """Outcome of a CSV import. Every created post is a draft."""
    created: int
    failed: int
    post_ids: List[str]
    errors: List[Dict[str, Any]]


class CreateFlowRequest(TypedDict, total=False):
    name: str
    description: str
    account_id: str
    platform_user_id: str
    platform: str
    trigger: Dict[str, Any]


class ContentInsights(TypedDict, total=False):
    """What has worked on your published posts: format, weekday and pillar compared with your average."""
    version: str
    window_weeks: int
    posts_analyzed: int
    account_avg_engagement_rate: float
    sufficient: bool
    cells: List[Dict[str, Any]]
    top_posts: List[Dict[str, Any]]
    bottom_posts: List[Dict[str, Any]]
    rationales: List[str]


class Webhook(TypedDict, total=False):
    """An outbound webhook subscription. Deliveries are signed with the signing secret."""
    id: str
    target_url: str
    events: List["WebhookEvent"]
    integration_type: "WebhookIntegrationType"
    active: bool
    account_ids: List[str]
    consecutive_failures: int
    disabled_at: Union[str, None]
    disabled_reason: Union[str, None]
    last_delivery_at: Union[str, None]
    last_status: Union[int, None]
    last_error: Union[str, None]
    created_at: str
    updated_at: str


class CreateWebhookRequest(TypedDict, total=False):
    target_url: str
    events: List["WebhookEvent"]
    integration_type: "WebhookIntegrationType"
    account_ids: List[str]


class UpdateWebhookRequest(TypedDict, total=False):
    target_url: str
    events: List["WebhookEvent"]
    account_ids: List[str]
    active: bool


class Device(TypedDict, total=False):
    id: str
    platform: Literal["ios", "android"]
    app_version: str
    locale: str
    apns_environment: Literal["production", "sandbox"]
    last_seen_at: str
    created_at: str


class RegisterDeviceRequest(TypedDict, total=False):
    token: str
    platform: Literal["ios", "android"]
    app_version: str
    locale: str
    apns_environment: Literal["production", "sandbox"]


class PresignUploadRequest(TypedDict, total=False):
    filename: str
    mime_type: Literal["image/jpeg", "image/png", "image/webp", "video/mp4", "video/quicktime"]
    size_bytes: int


class PresignUploadResponse(TypedDict, total=False):
    key: str
    upload_url: str
    required_headers: Dict[str, str]
    public_url: str
    expires_at: str


class VerifyUploadRequest(TypedDict, total=False):
    key: str
    purpose: Literal["scheduler"]
    filename: str


class VerifyUploadResponse(TypedDict, total=False):
    verified: Any
    size_bytes: int
    public_url: str
    asset_id: str


class UploadFromUrlRequest(TypedDict, total=False):
    url: str


class UploadFromUrlResponse(TypedDict, total=False):
    url: str
    key: str
    size_bytes: int
    mime_type: Literal["image/jpeg", "image/png", "image/webp", "video/mp4", "video/quicktime"]


class RegisterActivityRequest(TypedDict, total=False):
    push_token: str
    post_id_hash: str
    apns_environment: Literal["production", "sandbox"]
    bundle_id: str


class LiveActivityRegistration(TypedDict, total=False):
    id: str
    post_id_hash: str
    apns_environment: Literal["production", "sandbox"]
    bundle_id: str
    created_at: str
    last_seen_at: str


class MeFeedAccountHealth(TypedDict, total=False):
    id: str
    platform: str
    username: Union[str, None]
    status: str
    needs_attention: bool


class MeFeedResponse(TypedDict, total=False):
    posts_today: int
    unread_inbox_count: int
    error_count_24h: int
    account_health: List["MeFeedAccountHealth"]
    generated_at: str
    cached: bool


NotificationCategoryToggles = TypedDict("NotificationCategoryToggles", {
    "inbox.message": bool,
    "ai.handoff": bool,
    "flow.error": bool,
    "post.published": bool,
    "post.failed": bool,
}, total=False)


class QuietHoursWindow(TypedDict, total=False):
    start_minute: int
    end_minute: int
    timezone: str


class NotificationPreferences(TypedDict, total=False):
    categories: "NotificationCategoryToggles"
    quiet_hours: "QuietHoursWindow"
    updated_at: str


class NotificationPreferencesResponse(TypedDict, total=False):
    data: "NotificationPreferences"


class NotificationPreferencesPatch(TypedDict, total=False):
    categories: "NotificationCategoryToggles"
    quiet_hours: "QuietHoursWindow"


class PostAutomationError(TypedDict, total=False):
    error: str
    code: str


class PostAutomationBlank(TypedDict, total=False):
    nodeId: str
    nodeName: str
    token: str
    context: str
    link: bool


class PostAutomationDraftPreview(TypedDict, total=False):
    flow_id: str
    state: str
    snapshot: Union[Dict[str, Any], None]
    steps: List[str]
    blanks: List["PostAutomationBlank"]
    content_hash: str
    error: Dict[str, Any]


class PostAutomationPreflight(TypedDict, total=False):
    ok: bool
    code: str
    message: str
    blanks: List["PostAutomationBlank"]
    upgradeRequired: bool
    retryable: bool


class PostAutomationTemplate(TypedDict, total=False):
    id: str
    name: str
    outcome_label: str
    outcome: str
    input_fields: List[Dict[str, Any]]
    default_inputs: Dict[str, Any]


class CreatePostAutomationDraftRequest(TypedDict, total=False):
    """Exactly the fields of one door; any other field is rejected with 400 invalid_body."""
    door: Literal["funnel", "template", "prompt"]
    account_id: str
    keyword: str
    link: str
    template_id: str
    inputs: Dict[str, Any]
    prompt: str


class ReviewDecision(TypedDict, total=False):
    kind: str
    reviewer_name: str
    comment: str
    created_at: str


class ReviewLink(TypedDict, total=False):
    id: str
    post_id: str
    url: str
    reviewer_name: str
    state: str
    expires_at: str
    revoked_at: str
    decisions: List["ReviewDecision"]
    created_at: str


class ReviewSummary(TypedDict, total=False):
    links: List["ReviewLink"]
    latest_decision: "ReviewDecision"
    approved_before_last_edit: bool


class ReviewLinkError(TypedDict, total=False):
    error: str
    code: str


class PostQuickStatsEnvelope(TypedDict, total=False):
    """The latest analytics of each target of one post."""
    data: Dict[str, Any]


class MediaAsset(TypedDict, total=False):
    id: str
    kind: Literal["image", "video"]
    url: str
    r2_key: str
    filename: str
    mime_type: str
    size_bytes: int
    width: int
    height: int
    duration_ms: int
    tags: List[str]
    used_in_count: int
    origin: Literal["upload", "ai_image", "backfill"]
    created_at: str


class MediaLibraryPage(TypedDict, total=False):
    items: List["MediaAsset"]
    next_cursor: Union[str, None]


class Plug(TypedDict, total=False):
    id: str
    post_id: str
    account_id: str
    trigger: Dict[str, Any]
    action: Dict[str, Any]
    state: Literal["armed", "fired", "expired", "failed"]
    last_value: int
    last_checked_at: str
    fired_at: str
    expires_at: str
    error: Dict[str, Any]
    created_at: str


class AiImageAllowance(TypedDict, total=False):
    used: int
    limit: Union[int, None]
    remaining: Union[int, None]
    resetAt: str


class GeneratedImage(TypedDict, total=False):
    asset_id: str
    url: str
    width: int
    height: int
    mime_type: str


class GenerateImageRequest(TypedDict, total=False):
    prompt: str
    caption: str
    fromCaption: bool
    aspect: Literal["square", "portrait", "landscape"]
    count: int
    requestId: str


class GenerateImageResponse(TypedDict, total=False):
    images: List["GeneratedImage"]
    failed: int
    allowance: "AiImageAllowance"


class LinkClicks(TypedDict, total=False):
    post_id: str
    links: List[Dict[str, Any]]


class Signature(TypedDict, total=False):
    id: str
    name: str
    text: str
    account_ids: Union[Literal["all"], List[str]]
    is_default: bool
    created_at: str
    updated_at: str


class PostingSlot(TypedDict, total=False):
    id: str
    account_ids: List[str]
    weekday: int
    minutes: int
    timezone: str
    created_at: str
    updated_at: str


class ClientInviteAccount(TypedDict, total=False):
    id: str
    platform: str
    username: str


class ClientInvite(TypedDict, total=False):
    id: str
    group_id: str
    group_name: str
    platforms: List[str]
    max_accounts: int
    used_account_ids: List[str]
    accounts: List["ClientInviteAccount"]
    url: str
    state: str
    expires_at: str
    revoked_at: str
    created_at: str


class ClientInviteError(TypedDict, total=False):
    error: str
    code: str


class RssFeed(TypedDict, total=False):
    _id: str
    url: str
    platforms: List[str]
    active: bool
    paused: bool
    stopped_after_errors: bool
    last_polled_at: Union[str, None]
    last_item_id: Union[str, None]
    error_count: int
    mode: Literal["draft", "ai_draft", "ai_schedule"]
    template: "RssFeedTemplate"
    image: Literal["none", "feed", "ai"]
    account_ids: List[str]
    daily_cap: int


class PlatformCatalogOptionField(TypedDict, total=False):
    key: str
    label: str
    type: str
    required: bool
    placeholder: str
    help: str
    choices: List[Dict[str, Any]]
    maxLength: int
    maxItems: int
    maxItemLength: int
    defaultValue: str
    contentTypes: List[str]


class PlatformCatalogEntry(TypedDict, total=False):
    id: str
    label: str
    iosGlyph: str
    connectKind: str
    approval: Dict[str, Any]
    content: Dict[str, Any]
    accountTextLimits: Dict[str, int]
    media: Dict[str, Any]
    options: List["PlatformCatalogOptionField"]
    destinations: Dict[str, Any]
    idempotency: str
    article: Dict[str, Any]
    metrics: bool
    connectForm: Dict[str, Any]


class PlatformCatalog(TypedDict, total=False):
    data: List["PlatformCatalogEntry"]


class PlatformDestination(TypedDict, total=False):
    id: str
    label: str
    description: str


class BulkPostActionRequest(TypedDict, total=False):
    action: Literal["schedule", "delete", "update_status"]
    post_ids: List[str]
    scheduled_for: str
    timezone: str
    status: Literal["draft", "scheduled"]


class PlugTarget(TypedDict, total=False):
    account_id: str
    platform: str
    metrics: List[Literal["likes", "comments", "reposts", "views"]]
    actions: List[Literal["repost", "comment"]]
    max_comment_length: int
    published: bool


class PostPlugs(TypedDict, total=False):
    plugs: List["Plug"]
    targets: List["PlugTarget"]
    limits: Dict[str, Any]


class ArmPlugRequest(TypedDict, total=False):
    account_id: str
    trigger: Dict[str, Any]
    action: Dict[str, Any]


class SignatureList(TypedDict, total=False):
    signatures: List["Signature"]
    limit: int


class CreateSignatureRequest(TypedDict, total=False):
    name: str
    text: str
    account_ids: Union[Literal["all"], List[str]]
    is_default: bool


class UpdateSignatureRequest(TypedDict, total=False):
    name: str
    text: str
    account_ids: Union[Literal["all"], List[str]]
    is_default: bool


class CreatePostingSlotRequest(TypedDict, total=False):
    account_ids: List[str]
    weekday: int
    minutes: int
    time: str
    timezone: str


class UpdatePostingSlotRequest(TypedDict, total=False):
    account_ids: List[str]
    weekday: int
    minutes: int
    time: str
    timezone: str


class SlotOccurrence(TypedDict, total=False):
    slot_id: str
    at: str
    account_ids: List[str]
    timezone: str
    free: bool


class FreeSlot(TypedDict, total=False):
    at: str
    slot_id: str
    timezone: str
    reserved_until: str


class CreateRssFeedRequest(TypedDict, total=False):
    url: str
    platforms: List[str]
    mode: Literal["draft", "ai_draft", "ai_schedule"]
    template: "RssFeedTemplate"
    image: Literal["none", "feed", "ai"]
    account_ids: List[str]
    daily_cap: int


class UpdateRssFeedRequest(TypedDict, total=False):
    platforms: List[str]
    paused: bool
    mode: Literal["draft", "ai_draft", "ai_schedule"]
    template: "RssFeedTemplate"
    image: Literal["none", "feed", "ai"]
    account_ids: List[str]
    daily_cap: int


class PlatformDestinationList(TypedDict, total=False):
    mode: Literal["list", "manual"]
    destinations: List["PlatformDestination"]


# Non-object schemas. Refs are quoted so these can name classes defined above in any order.
WebhookEvent = Literal["message.received", "comment.received", "flow.triggered", "flow.completed", "flow.error", "post.published", "post.failed", "post.review_decision", "post.plug_fired", "account.disconnected", "whatsapp.template_status"]
WebhookIntegrationType = Literal["webhook", "custom", "n8n", "make", "zapier"]
RssFeedTemplate = Union[Dict[str, Any], None]
