import React from "react";

import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Box,
  Check,
  ChevronRight,
  CircleDot,
  FileText,
  Fingerprint,
  Globe,
  LayoutDashboard,
  Menu,
  Network,
  Radio,
  Search,
  Server,
  Shield,
  ShieldCheck,
  Terminal,
  Wifi,
  X,
} from "lucide-react";

import "./App.css";

const API_BASE = "http://localhost:8000/api/v1";

const ENGAGEMENT_ID =
  "63ea0426-1463-43dd-b5cd-e875e3391409";

const TESTING_TAXONOMY = {
  recon: [
    "dns",
    "subdomain_discovery",
    "technology_discovery",
  ],
  network: [
    "port_enumeration",
    "service_enumeration",
    "network_configuration",
  ],
  web: [
    "authentication",
    "authorization",
    "session_management",
    "input_validation",
    "business_logic",
  ],
  api: [
    "authentication",
    "authorization",
    "object_level_authorization",
    "rate_limiting",
    "input_validation",
  ],
} as const;

const EXECUTABLE_TEST = {
  area: "network",
  test: "service_enumeration",
} as const;

type View =
  | "overview"
  | "attack-surface"
  | "testing"
  | "activities"
  | "findings"
  | "evidence"
  | "coverage"
  | "reports";

type Asset = {
  id: string;
  engagement_id: string;
  value: string;
  asset_type: string;
  status: string;
  description: string | null;
  created_at: string;
};

type Scope = {
  id: string;
  engagement_id: string;
  target: string;
  target_type: string;
  scope_type: "include" | "exclude";
  description: string | null;
  created_at: string;
};

type Service = {
  id: string;
  engagement_id: string;
  asset_id: string;
  service: string;
  port: number;
  protocol: string;
  state: string;
  created_at: string;
};

type AssetRelationship = {
  id: string;
  engagement_id: string;
  source_asset_id: string;
  target_asset_id: string;
  relationship_type: string;
  description: string | null;
  created_at: string;
};

type Finding = {
  id: string;
  engagement_id: string;
  asset_id: string | null;
  activity_id: string | null;
  evidence_id: string | null;
  title: string;
  description: string | null;
  severity: string;
  status: string;
  validation_status: string;
  remediation: string | null;
  retest_status: string | null;
  retest_activity_id: string | null;
  retest_evidence_id: string | null;
  created_at: string;
};

type FindingProvenance = {
  finding: {
    id: string;
    title: string;
    severity: string;
    status: string;
    validation_status: string;
  };
  asset: {
    id: string;
    value: string;
    asset_type: string;
  } | null;
  activity: {
    id: string;
    activity_type: string;
    testing_area: string | null;
    test_type: string | null;
    title: string;
    description: string | null;
    command: string | null;
    tool: string | null;
    status: string;
    created_at: string;
  } | null;
  evidence: {
    id: string;
    evidence_type: string;
    title: string;
    content: string | null;
    file_path: string | null;
    created_at: string;
  } | null;
};

type Evidence = {
  id: string;
  engagement_id: string;
  activity_id: string | null;
  asset_id: string | null;
  evidence_type: string;
  title: string;
  content: string;
  file_path: string | null;
  created_at: string;
};

type ActivityRecord = {
  id: string;
  engagement_id: string;
  asset_id: string | null;
  activity_type: string;
  title: string;
  description: string | null;
  command: string | null;
  tool: string | null;
  status: string;
  created_at: string;
};

type ToolEventResponse = {
  tool: string;
  target: string;
  return_code: number;
  activity_id: string;
  evidence_id: string;
  testing_area: string | null;
  test_type: string | null;
  discovered_services: Array<{
    id: string;
    port: number;
    protocol: string;
    state: string;
    service: string;
  }>;
};

type CoverageFinding = {
  id: string;
  title: string;
  severity: string;
  status: string;
  validation_status: string;
};

type CoverageEvidence = {
  id: string;
  evidence_type: string;
  title: string;
  content: string | null;
  file_path: string | null;
  created_at: string;
  findings: CoverageFinding[];
};

type CoverageActivity = {
  id: string;
  asset_id: string | null;
  activity_type: string;
  testing_area: string | null;
  test_type: string | null;
  title: string;
  description: string | null;
  command: string | null;
  tool: string | null;
  status: string;
  created_at: string;
  evidence: CoverageEvidence[];
  findings: CoverageFinding[];
};

type CoverageTraceability = {
  engagement_id: string;
  testing_area: string;
  test_type: string;
  status: "tested" | "untested";
  activity_count: number;
  activities: CoverageActivity[];
};

type Dashboard = {
  engagement: {
    id: string;
    name: string;
    client: string;
    status: string;
    description: string;
    created_at: string;
  };

  assets: {
    total: number;
    in_scope: number;
    excluded: number;
  };

  services: {
    total: number;
    in_scope: number;
    open: number;
    http: number;
    https: number;
  };

  testing: {
    tested: number;
    untested: number;
    coverage: Record<
      string,
      Record<string, string>
    >;
  };

  findings: {
    total: number;
    validated: number;
    open: number;
    closed: number;
  };

  activities: number;
  evidence_items: number;
};

const fallbackDashboard: Dashboard = {
  engagement: {
    id: ENGAGEMENT_ID,
    name: "ACME Web Application Pentest",
    client: "ACME Corporation",
    status: "active",
    description:
      "External web application security assessment",
    created_at: "",
  },

  assets: {
    total: 0,
    in_scope: 0,
    excluded: 0,
  },

  services: {
    total: 0,
    in_scope: 0,
    open: 0,
    http: 0,
    https: 0,
  },

  testing: {
    tested: 0,
    untested: 16,
    coverage: {},
  },

  findings: {
    total: 0,
    validated: 0,
    open: 0,
    closed: 0,
  },

  activities: 0,
  evidence_items: 0,
};

async function fetchJson<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_BASE}${path}`,
    options,
  );

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status}`,
    );
  }

  return response.json();
}

function StatCard({
  icon,
  label,
  value,
  detail,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  detail: string;
}) {
  return (
    <div className="stat-card">
      <div className="stat-icon">
        {icon}
      </div>

      <div className="stat-content">
        <span>{label}</span>

        <strong>
          {value.toString().padStart(2, "0")}
        </strong>

        <small>{detail}</small>
      </div>
    </div>
  );
}

function ScopeBadge({
  type,
}: {
  type: "include" | "exclude" | "unknown";
}) {
  if (type === "include") {
    return (
      <span className="scope-badge scope-in">
        <span />
        IN SCOPE
      </span>
    );
  }

  if (type === "exclude") {
    return (
      <span className="scope-badge scope-excluded">
        <span />
        EXCLUDED
      </span>
    );
  }

  return (
    <span className="scope-badge scope-unknown">
      <span />
      NOT EXPLICITLY SCOPED
    </span>
  );
}

function App() {
  const [view, setView] =
    React.useState<View>("overview");

  const [dashboard, setDashboard] =
    React.useState<Dashboard>(
      fallbackDashboard,
    );

  const [assets, setAssets] =
    React.useState<Asset[]>([]);

  const [services, setServices] =
    React.useState<Service[]>([]);

  const [scopes, setScopes] =
    React.useState<Scope[]>([]);

  const [assetRelationships, setAssetRelationships] =
    React.useState<AssetRelationship[]>([]);

  const [findings, setFindings] =
    React.useState<Finding[]>([]);

  const [activities, setActivities] =
    React.useState<ActivityRecord[]>([]);

  const [activitiesLoading, setActivitiesLoading] =
    React.useState(false);

  const [activitiesError, setActivitiesError] =
    React.useState<string | null>(null);

  const [activitySearch, setActivitySearch] =
    React.useState("");

  const [activityFilter, setActivityFilter] =
    React.useState<
      "all" | "recon" | "network" | "web" | "api" | "retest"
    >("all");

  const [selectedActivityId, setSelectedActivityId] =
    React.useState<string | null>(null);

  const [selectedFindingId, setSelectedFindingId] =
    React.useState<string | null>(null);

  const [findingProvenance, setFindingProvenance] =
    React.useState<FindingProvenance | null>(null);

  const [findingProvenanceLoading, setFindingProvenanceLoading] =
    React.useState(false);

  const [findingProvenanceError, setFindingProvenanceError] =
    React.useState<string | null>(null);

  const [findingSearch, setFindingSearch] =
    React.useState("");

  const [findingFilter, setFindingFilter] =
    React.useState<
      "all" | "open" | "closed" | "validated" | "unvalidated"
    >("all");

  const [findingsLoading, setFindingsLoading] =
    React.useState(false);

  const [findingsError, setFindingsError] =
    React.useState<string | null>(null);

  const [evidence, setEvidence] =
    React.useState<Evidence[]>([]);

  const [evidenceLoading, setEvidenceLoading] =
    React.useState(false);

  const [evidenceError, setEvidenceError] =
    React.useState<string | null>(null);

  const [selectedEvidenceId, setSelectedEvidenceId] =
    React.useState<string | null>(null);

  const [evidenceSearch, setEvidenceSearch] =
    React.useState("");

  const [evidenceFilter, setEvidenceFilter] =
    React.useState<"all" | "command_output" | "retest">("all");

  const [findingActionLoading, setFindingActionLoading] =
    React.useState(false);

  const [findingActionError, setFindingActionError] =
    React.useState<string | null>(null);

  const [, setLoading] =
  React.useState(true);

  const [surfaceLoading, setSurfaceLoading] =
    React.useState(false);

  const [error, setError] =
    React.useState<string | null>(null);

  const [surfaceError, setSurfaceError] =
    React.useState<string | null>(null);

  const [testAssetId, setTestAssetId] =
    React.useState<string | null>(null);

  const [testTool, setTestTool] =
    React.useState<"nmap" | "mock">("nmap");

  const [testTitle, setTestTitle] =
    React.useState("Service enumeration");

  const [testRunning, setTestRunning] =
    React.useState(false);

  const [testError, setTestError] =
    React.useState<string | null>(null);

  const [testResult, setTestResult] =
    React.useState<ToolEventResponse | null>(null);

  const [mobileMenuOpen, setMobileMenuOpen] =
    React.useState(false);

  const [selectedAssetId, setSelectedAssetId] =
    React.useState<string | null>(null);

  const [assetSearch, setAssetSearch] =
    React.useState("");

  const [scopeFilter, setScopeFilter] =
    React.useState<
      "all" | "include" | "exclude" | "unknown"
    >("all");

  const [coverageTrace, setCoverageTrace] =
    React.useState<CoverageTraceability | null>(null);

  const [coverageTraceLoading, setCoverageTraceLoading] =
    React.useState(false);

  const [coverageTraceError, setCoverageTraceError] =
    React.useState<string | null>(null);

  const [selectedCoverageItem, setSelectedCoverageItem] =
    React.useState<{
      area: string;
      test: string;
    } | null>(null);

  const [selectedTestingItem, setSelectedTestingItem] =
    React.useState<{
      area: string;
      test: string;
    }>({
      area: EXECUTABLE_TEST.area,
      test: EXECUTABLE_TEST.test,
    });

  const [testingTrace, setTestingTrace] =
    React.useState<CoverageTraceability | null>(null);

  const [testingTraceLoading, setTestingTraceLoading] =
    React.useState(false);

  const [testingTraceError, setTestingTraceError] =
    React.useState<string | null>(null);

  const [testingTraceVersion, setTestingTraceVersion] =
    React.useState(0);

  React.useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);

        const [
          dashboardData,
          servicesData,
          findingsData,
        ] = await Promise.all([
          fetchJson<Dashboard>(
            `/engagements/${ENGAGEMENT_ID}/dashboard`,
          ),

          fetchJson<Service[]>(
            `/engagements/${ENGAGEMENT_ID}/services`,
          ),

          fetchJson<Finding[]>(
            `/engagements/${ENGAGEMENT_ID}/findings`,
          ),
        ]);

        setDashboard(dashboardData);
        setServices(servicesData);
        setFindings(findingsData);

        setError(null);
      } catch (err) {
        console.error(err);

        setError(
          "Unable to reach VANTA backend",
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  React.useEffect(() => {
    if (view !== "activities") {
      return;
    }

    async function loadActivities() {
      try {
        setActivitiesLoading(true);

        const data = await fetchJson<ActivityRecord[]>(
          `/engagements/${ENGAGEMENT_ID}/activities`,
        );

        setActivities(data);
        setActivitiesError(null);

        if (!selectedActivityId && data.length > 0) {
          setSelectedActivityId(data[0].id);
        }
      } catch (err) {
        console.error(err);
        setActivitiesError(
          "Unable to load assessment activities",
        );
      } finally {
        setActivitiesLoading(false);
      }
    }

    loadActivities();
  }, [view]);

  React.useEffect(() => {
    if (view !== "findings") {
      return;
    }

    async function loadFindingsWorkspace() {
      try {
        setFindingsLoading(true);

        const [findingsData, assetsData] =
          await Promise.all([
            fetchJson<Finding[]>(
              `/engagements/${ENGAGEMENT_ID}/findings`,
            ),
            fetchJson<Asset[]>(
              `/engagements/${ENGAGEMENT_ID}/assets`,
            ),
          ]);

        setFindings(findingsData);
        setAssets(assetsData);
        setFindingsError(null);

        if (
          !selectedFindingId &&
          findingsData.length > 0
        ) {
          setSelectedFindingId(
            findingsData[0].id,
          );
        }
      } catch (err) {
        console.error(err);
        setFindingsError(
          "Unable to load assessment findings",
        );
      } finally {
        setFindingsLoading(false);
      }
    }

    loadFindingsWorkspace();
  }, [view]);

  React.useEffect(() => {
    if (view !== "findings" || !selectedFindingId) {
      setFindingProvenance(null);
      setFindingProvenanceError(null);
      return;
    }

    async function loadFindingProvenance() {
      try {
        setFindingProvenanceLoading(true);

        const data = await fetchJson<FindingProvenance>(
          `/engagements/${ENGAGEMENT_ID}/findings/${selectedFindingId}/provenance`,
        );

        setFindingProvenance(data);
        setFindingProvenanceError(null);
      } catch (err) {
        console.error(err);
        setFindingProvenance(null);
        setFindingProvenanceError(
          "Unable to load finding provenance",
        );
      } finally {
        setFindingProvenanceLoading(false);
      }
    }

    loadFindingProvenance();
  }, [view, selectedFindingId]);

  React.useEffect(() => {
    if (view !== "evidence") {
      return;
    }

    async function loadEvidenceWorkspace() {
      try {
        setEvidenceLoading(true);

        const data = await fetchJson<Evidence[]>(
          `/engagements/${ENGAGEMENT_ID}/evidence`,
        );

        setEvidence(data);
        setEvidenceError(null);

        if (!selectedEvidenceId && data.length > 0) {
          setSelectedEvidenceId(data[0].id);
        }
      } catch (err) {
        console.error(err);
        setEvidenceError(
          "Unable to load assessment evidence",
        );
      } finally {
        setEvidenceLoading(false);
      }
    }

    loadEvidenceWorkspace();
  }, [view]);

  React.useEffect(() => {
    if (view !== "attack-surface") {
      return;
    }

    async function loadAttackSurface() {
      try {
        setSurfaceLoading(true);

        const [
          assetsData,
          servicesData,
          scopesData,
          relationshipsData,
          findingsData,
          evidenceData,
        ] = await Promise.all([
          fetchJson<Asset[]>(
            `/engagements/${ENGAGEMENT_ID}/assets`,
          ),

          fetchJson<Service[]>(
            `/engagements/${ENGAGEMENT_ID}/services`,
          ),

          fetchJson<Scope[]>(
            `/engagements/${ENGAGEMENT_ID}/scope`,
          ),

          fetchJson<AssetRelationship[]>(
            `/engagements/${ENGAGEMENT_ID}/relationships`,
          ),

          fetchJson<Finding[]>(
            `/engagements/${ENGAGEMENT_ID}/findings`,
          ),

          fetchJson<Evidence[]>(
            `/engagements/${ENGAGEMENT_ID}/evidence`,
          ),
        ]);

        setAssets(assetsData);
        setServices(servicesData);
        setScopes(scopesData);
        setAssetRelationships(relationshipsData);
        setFindings(findingsData);
        setEvidence(evidenceData);

        setSurfaceError(null);

        if (
          !selectedAssetId &&
          assetsData.length > 0
        ) {
          setSelectedAssetId(
            assetsData[0].id,
          );
        }
      } catch (err) {
        console.error(err);

        setSurfaceError(
          "Unable to load attack surface",
        );
      } finally {
        setSurfaceLoading(false);
      }
    }

    loadAttackSurface();
  }, [view]);

  React.useEffect(() => {
    if (view !== "testing" || !selectedTestingItem) {
      setTestingTrace(null);
      setTestingTraceError(null);
      return;
    }

    const testingItem = selectedTestingItem;

    async function loadTestingTraceability() {
      try {
        setTestingTraceLoading(true);
        setTestingTraceError(null);

        const data = await fetchJson<CoverageTraceability>(
          `/engagements/${ENGAGEMENT_ID}/coverage/${testingItem.area}/${testingItem.test}`,
        );

        setTestingTrace(data);
      } catch (err) {
        console.error(err);
        setTestingTrace(null);
        setTestingTraceError(
          "Unable to load testing traceability",
        );
      } finally {
        setTestingTraceLoading(false);
      }
    }

    loadTestingTraceability();
  }, [view, selectedTestingItem, testingTraceVersion]);

  React.useEffect(() => {
    if (view !== "coverage" || !selectedCoverageItem) {
      setCoverageTrace(null);
      setCoverageTraceError(null);
      return;
    }

    const coverageItem = selectedCoverageItem;

    async function loadCoverageTraceability() {
      try {
        setCoverageTraceLoading(true);
        setCoverageTraceError(null);

        const data = await fetchJson<CoverageTraceability>(
          `/engagements/${ENGAGEMENT_ID}/coverage/${coverageItem.area}/${coverageItem.test}`,
        );

        setCoverageTrace(data);
      } catch (err) {
        console.error(err);
        setCoverageTrace(null);
        setCoverageTraceError(
          "Unable to load coverage traceability",
        );
      } finally {
        setCoverageTraceLoading(false);
      }
    }

    loadCoverageTraceability();
  }, [view, selectedCoverageItem]);

  function coverageTestLabel(value: string) {
    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  const coverageTotal =
    dashboard.testing.tested +
    dashboard.testing.untested;

  const coveragePercent =
    coverageTotal > 0
      ? Math.round(
          (dashboard.testing.tested /
            coverageTotal) *
            100,
        )
      : 0;

  function getScopeType(
    asset: Asset,
  ): "include" | "exclude" | "unknown" {
    const exactMatch = scopes.find(
      (scope) =>
        scope.target.toLowerCase() ===
        asset.value.toLowerCase(),
    );

    if (!exactMatch) {
      return "unknown";
    }

    return exactMatch.scope_type;
  }

  function getAssetServices(
    assetId: string,
  ) {
    return services.filter(
      (service) =>
        service.asset_id === assetId,
    );
  }

  const filteredAssets = assets.filter(
    (asset) => {
      const scopeType =
        getScopeType(asset);

      const matchesScope =
        scopeFilter === "all" ||
        scopeType === scopeFilter;

      const query =
        assetSearch.trim().toLowerCase();

      if (!query) {
        return matchesScope;
      }

      const assetServices =
        getAssetServices(asset.id);

      const matchesAsset =
        asset.value
          .toLowerCase()
          .includes(query) ||
        asset.asset_type
          .toLowerCase()
          .includes(query) ||
        (asset.description ?? "")
          .toLowerCase()
          .includes(query);

      const matchesService =
        assetServices.some(
          (service) =>
            service.service
              .toLowerCase()
              .includes(query) ||
            service.port
              .toString()
              .includes(query) ||
            service.protocol
              .toLowerCase()
              .includes(query),
        );

      return (
        matchesScope &&
        (matchesAsset ||
          matchesService)
      );
    },
  );

  const selectedAsset =
    assets.find(
      (asset) =>
        asset.id === selectedAssetId,
    ) ?? null;

  const selectedServices =
    selectedAsset
      ? getAssetServices(
          selectedAsset.id,
        )
      : [];

  const selectedRelationships =
    selectedAsset
      ? assetRelationships.filter(
          (relationship) =>
            relationship.source_asset_id ===
              selectedAsset.id ||
            relationship.target_asset_id ===
              selectedAsset.id,
        )
      : [];

  function getRelationshipAsset(
    relationship: AssetRelationship,
    direction: "source" | "target",
  ) {
    const assetId =
      direction === "source"
        ? relationship.source_asset_id
        : relationship.target_asset_id;

    return assets.find(
      (asset) => asset.id === assetId,
    );
  }

  type ActivityArea =
    | "recon"
    | "network"
    | "web"
    | "api"
    | "retest";

  function activityArea(
    activity: ActivityRecord,
  ): ActivityArea {
    if (activity.activity_type === "retest") {
      return "retest";
    }

    if (activity.tool === "nmap") {
      return "network";
    }

    if (
      activity.tool === "mock" ||
      activity.tool === "mock-tool"
    ) {
      return "recon";
    }

    const text = [
      activity.title,
      activity.description ?? "",
      activity.command ?? "",
      activity.tool ?? "",
    ]
      .join(" ")
      .toLowerCase();

    if (/\bapi\b/.test(text)) {
      return "api";
    }

    return "web";
  }

  function activityAreaLabel(activity: ActivityRecord) {
    const area = activityArea(activity);

    if (area === "retest") return "RETEST";
    if (area === "network") return "NETWORK";
    if (area === "recon") return "RECON";
    if (area === "api") return "API";
    return "WEB";
  }

  function activityAssetName(activity: ActivityRecord) {
    if (!activity.asset_id) {
      return "ENGAGEMENT";
    }

    return (
      assets.find(
        (asset) => asset.id === activity.asset_id,
      )?.value ??
      (activity.asset_id ===
      "72b0dd6e-be9d-425a-86a8-41e70c779b50"
        ? "example.com"
        : "UNKNOWN ASSET")
    );
  }

  function formatActivityTime(value: string) {
    const date = new Date(value);

    return date.toLocaleString([], {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  const filteredActivities = activities.filter(
    (activity) => {
      const area = activityArea(activity);

      if (
        activityFilter !== "all" &&
        area !== activityFilter
      ) {
        return false;
      }

      const query = activitySearch.trim().toLowerCase();

      if (!query) {
        return true;
      }

      return [
        activity.title,
        activity.description ?? "",
        activity.command ?? "",
        activity.tool ?? "",
        activity.status,
        activityAssetName(activity),
        activity.activity_type,
      ].some((value) =>
        value.toLowerCase().includes(query),
      );
    },
  );

  const selectedActivity =
    activities.find(
      (activity) =>
        activity.id === selectedActivityId,
    ) ?? null;

  function findingAssetName(finding: Finding) {
    if (!finding.asset_id) {
      return "ENGAGEMENT";
    }

    return (
      assets.find(
        (asset) => asset.id === finding.asset_id,
      )?.value ??
      (finding.asset_id ===
      "72b0dd6e-be9d-425a-86a8-41e70c779b50"
        ? "example.com"
        : "UNKNOWN ASSET")
    );
  }

  function findingSeverityClass(severity: string) {
    const value = severity.toLowerCase();

    if (value === "critical") return "critical";
    if (value === "high") return "high";
    if (value === "medium") return "medium";
    if (value === "low") return "low";
    return "informational";
  }

  function findingValidationLabel(status: string) {
    return status.replace(/_/g, " ").toUpperCase();
  }

  function formatFindingDate(value: string) {
    if (!value) {
      return "—";
    }

    return new Date(value).toLocaleString([], {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  const filteredFindings = findings.filter(
    (finding) => {
      const filter = findingFilter;

      if (filter === "open" && finding.status !== "open") {
        return false;
      }

      if (
        filter === "closed" &&
        finding.status !== "closed"
      ) {
        return false;
      }

      if (
        filter === "validated" &&
        finding.validation_status !== "validated"
      ) {
        return false;
      }

      if (
        filter === "unvalidated" &&
        finding.validation_status === "validated"
      ) {
        return false;
      }

      const query =
        findingSearch.trim().toLowerCase();

      if (!query) {
        return true;
      }

      return [
        finding.title,
        finding.description ?? "",
        finding.severity,
        finding.status,
        finding.validation_status,
        findingAssetName(finding),
      ].some((value) =>
        value.toLowerCase().includes(query),
      );
    },
  );

  function evidenceAssetName(item: Evidence) {
    if (!item.asset_id) {
      return "ENGAGEMENT";
    }

    return (
      assets.find((asset) => asset.id === item.asset_id)?.value ??
      (item.asset_id ===
      "72b0dd6e-be9d-425a-86a8-41e70c779b50"
        ? "example.com"
        : "UNKNOWN ASSET")
    );
  }

  function formatEvidenceDate(value: string) {
    if (!value) return "—";

    return new Date(value).toLocaleString([], {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  const filteredEvidence = evidence.filter((item) => {
    if (evidenceFilter !== "all" && item.evidence_type !== evidenceFilter) {
      return false;
    }

    const query = evidenceSearch.trim().toLowerCase();
    if (!query) return true;

    return [
      item.title,
      item.evidence_type,
      item.content,
      evidenceAssetName(item),
      item.activity_id ?? "",
    ].some((value) => value.toLowerCase().includes(query));
  });

  const selectedEvidence =
    evidence.find((item) => item.id === selectedEvidenceId) ?? null;

  const selectedFinding =
    findings.find(
      (finding) =>
        finding.id === selectedFindingId,
    ) ?? null;

  async function validateFinding(findingId: string) {
    try {
      setFindingActionLoading(true);
      setFindingActionError(null);

      const updated = await fetchJson<Finding>(
        `/engagements/${ENGAGEMENT_ID}/findings/${findingId}/validate`,
        {
          method: "POST",
        },
      );

      setFindings((current) =>
        current.map((finding) =>
          finding.id === updated.id
            ? updated
            : finding,
        ),
      );
    } catch (err) {
      console.error(err);
      setFindingActionError(
        "Unable to validate finding",
      );
    } finally {
      setFindingActionLoading(false);
    }
  }

  async function startFindingRetest(findingId: string) {
    try {
      setFindingActionLoading(true);
      setFindingActionError(null);

      const updated = await fetchJson<Finding>(
        `/engagements/${ENGAGEMENT_ID}/findings/${findingId}/retest`,
        {
          method: "POST",
        },
      );

      setFindings((current) =>
        current.map((finding) =>
          finding.id === updated.id
            ? updated
            : finding,
        ),
      );
    } catch (err) {
      console.error(err);
      setFindingActionError(
        "Unable to start finding retest",
      );
    } finally {
      setFindingActionLoading(false);
    }
  }

  async function setFindingRetestResult(
    findingId: string,
    result: "passed" | "failed",
  ) {
    try {
      setFindingActionLoading(true);
      setFindingActionError(null);

      const updated = await fetchJson<Finding>(
        `/engagements/${ENGAGEMENT_ID}/findings/${findingId}/retest/result`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ result }),
        },
      );

      setFindings((current) =>
        current.map((finding) =>
          finding.id === updated.id
            ? updated
            : finding,
        ),
      );
    } catch (err) {
      console.error(err);
      setFindingActionError(
        `Unable to set retest result to ${result}`,
      );
    } finally {
      setFindingActionLoading(false);
    }
  }

  React.useEffect(() => {
    setTestTitle(coverageTestLabel(selectedTestingItem.test));
  }, [selectedTestingItem]);

  React.useEffect(() => {
    if (assets.length === 0) {
      return;
    }

    if (!testAssetId || !assets.some((asset) => asset.id === testAssetId)) {
      setTestAssetId(assets[0].id);
    }
  }, [assets, testAssetId]);

  async function executeTest() {
    if (!testAssetId) {
      setTestError("Select an asset before executing a test.");
      return;
    }

    try {
      setTestRunning(true);
      setTestError(null);
      setTestResult(null);

      const result = await fetchJson<ToolEventResponse>(
        "/events/tool",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            engagement_id: ENGAGEMENT_ID,
            asset_id: testAssetId,
            tool: testTool,
            title: testTitle,
          }),
        },
      );

      setTestResult(result);

      const [servicesData, dashboardData] = await Promise.all([
        fetchJson<Service[]>(`/engagements/${ENGAGEMENT_ID}/services`),
        fetchJson<Dashboard>(`/engagements/${ENGAGEMENT_ID}/dashboard`),
      ]);

      setServices(servicesData);
      setDashboard(dashboardData);
      setTestingTraceVersion((current) => current + 1);
    } catch (err) {
      console.error(err);
      setTestError(
        err instanceof Error ? err.message : "Unable to execute security test",
      );
    } finally {
      setTestRunning(false);
    }
  }

  function navigate(nextView: View) {
    setView(nextView);
    setMobileMenuOpen(false);

    if (
      nextView === "attack-surface" &&
      !selectedAssetId &&
      assets.length > 0
    ) {
      setSelectedAssetId(assets[0].id);
    }
  }

  function closeMobileMenu() {
    setMobileMenuOpen(false);
  }

  return (
    <div className="vanta-app">
      {mobileMenuOpen && (
        <button
          className="mobile-overlay"
          onClick={closeMobileMenu}
          aria-label="Close navigation"
        />
      )}

      <aside
        className={`sidebar ${
          mobileMenuOpen
            ? "sidebar-open"
            : ""
        }`}
      >
        <div className="mobile-sidebar-header">
          <span>VANTA</span>

          <button
            className="sidebar-close"
            onClick={closeMobileMenu}
            aria-label="Close navigation"
          >
            <X size={19} />
          </button>
        </div>

        <div className="brand">
          <div className="brand-mark">
            V
          </div>

          <div className="brand-copy">
            <div className="brand-name">
              VANTA
            </div>

            <div className="brand-subtitle">
              SECURITY PLATFORM
            </div>
          </div>
        </div>

        <div className="workspace">
          <span className="workspace-label">
            ENGAGEMENT
          </span>

          <div className="workspace-name">
            <span>
              ACME / WEB-PENTEST
            </span>

            <ChevronRight size={14} />
          </div>
        </div>

        <nav className="navigation">
          <div className="nav-section">
            COMMAND CENTER
          </div>

          <button
            className={`nav-item ${
              view === "overview"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("overview")
            }
          >
            <LayoutDashboard size={17} />
            <span>Overview</span>
          </button>

          <button
            className={`nav-item ${
              view === "attack-surface"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("attack-surface")
            }
          >
            <Network size={17} />
            <span>Attack Surface</span>
          </button>

          <button
            className={`nav-item ${
              view === "testing"
                ? "active"
                : ""
            }`}
            onClick={() => navigate("testing")}
          >
            <Terminal size={17} />
            <span>Testing</span>
          </button>

          <button
            className={`nav-item ${
              view === "activities"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("activities")
            }
          >
            <Activity size={17} />
            <span>Activities</span>
          </button>

          <div className="nav-section">
            ASSESSMENT
          </div>

          <button
            className={`nav-item ${
              view === "findings"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("findings")
            }
          >
            <AlertTriangle size={17} />

            <span>Findings</span>

            <span className="nav-count">
              {dashboard.findings.total}
            </span>
          </button>

          <button
            className={`nav-item ${
              view === "evidence"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("evidence")
            }
          >
            <Fingerprint size={17} />
            <span>Evidence</span>
          </button>

          <button
            className={`nav-item ${
              view === "coverage"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("coverage")
            }
          >
            <ShieldCheck size={17} />
            <span>Coverage</span>
          </button>

          <div className="nav-section">
            OUTPUT
          </div>

          <button
            className="nav-item"
            onClick={() =>
              navigate("reports")
            }
          >
            <FileText size={17} />
            <span>Reports</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot" />

            <div>
              <strong>
                SYSTEM ONLINE
              </strong>

              <small>
                VANTA API CONNECTED
              </small>
            </div>
          </div>

          <div className="version">
            VANTA 0.1.0
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="mobile-brand">
            <button
              className="mobile-menu-button"
              onClick={() =>
                setMobileMenuOpen(true)
              }
              aria-label="Open navigation"
            >
              <Menu size={21} />
            </button>

            <div className="mobile-logo">
              V
            </div>

            <strong>VANTA</strong>
          </div>

          <div className="breadcrumb">
            <span>ENGAGEMENTS</span>

            <ChevronRight size={14} />

            <strong>
              {view === "attack-surface"
                ? "ATTACK SURFACE"
                : view === "testing"
                ? "TESTING"
                : view === "activities"
                ? "ACTIVITY LOG"
                : view === "findings"
                ? "FINDINGS"
                : view === "evidence"
                ? "EVIDENCE"
                : view === "coverage"
                ? "COVERAGE"
                : view === "reports"
                ? "REPORTS"
                : "ACME WEB APPLICATION PENTEST"}
            </strong>
          </div>

          <div className="topbar-actions">
            <div className="live-indicator">
              <span />
              LIVE
            </div>

            <button
              className="icon-button"
              aria-label="Search"
            >
              <Search size={17} />
            </button>

            <button
              className="profile-button"
              aria-label="Profile"
            >
              PA
            </button>
          </div>
        </header>

        {view === "overview" && (
          <section className="page">
            <div className="hero">
              <div className="hero-main">
                <div className="eyebrow">
                  <CircleDot size={12} />

                  ACTIVE SECURITY ASSESSMENT
                </div>

                <h1>
                  {dashboard.engagement.name}
                </h1>

                <p>
                  {
                    dashboard.engagement
                      .description
                  }
                </p>
              </div>

              <div className="hero-meta">
                <span>CLIENT</span>

                <strong>
                  {dashboard.engagement.client}
                </strong>
              </div>
            </div>

            {error && (
              <div className="error-banner">
                <AlertTriangle size={16} />

                {error}
              </div>
            )}

            <div className="stats-grid">
              <StatCard
                icon={<Box size={19} />}
                label="ASSETS"
                value={
                  dashboard.assets.total
                }
                detail={`${dashboard.assets.in_scope} in scope`}
              />

              <StatCard
                icon={<Server size={19} />}
                label="SERVICES"
                value={
                  dashboard.services.total
                }
                detail={`${dashboard.services.open} open`}
              />

              <StatCard
                icon={
                  <AlertTriangle size={19} />
                }
                label="FINDINGS"
                value={
                  dashboard.findings.total
                }
                detail={`${dashboard.findings.validated} validated`}
              />

              <StatCard
                icon={
                  <Fingerprint size={19} />
                }
                label="EVIDENCE"
                value={
                  dashboard.evidence_items
                }
                detail="captured artifacts"
              />
            </div>

            <div className="content-grid">
              <section className="panel attack-panel">
                <div className="panel-header">
                  <div>
                    <span className="panel-kicker">
                      ATTACK SURFACE
                    </span>

                    <h2>
                      Exposed Services
                    </h2>
                  </div>

                  <button
                    className="panel-action"
                    onClick={() =>
                      navigate(
                        "attack-surface",
                      )
                    }
                  >
                    VIEW ALL
                    <ChevronRight size={14} />
                  </button>
                </div>

                <button
                  className="asset-node overview-asset"
                  onClick={() =>
                    navigate(
                      "attack-surface",
                    )
                  }
                >
                  <div className="node-icon">
                    <Globe size={18} />
                  </div>

                  <div className="asset-node-info">
                    <strong>
                      example.com
                    </strong>

                    <span>
                      PRIMARY ASSESSMENT ASSET
                    </span>
                  </div>

                  <div className="node-status">
                    <span />
                    IN SCOPE
                  </div>
                </button>

                <div className="service-list">
                  {services
                    .filter(
                      (service) =>
                        service.asset_id ===
                        "72b0dd6e-be9d-425a-86a8-41e70c779b50",
                    )
                    .map(
                      (service) => (
                        <div
                          className="service-row"
                          key={service.id}
                        >
                          <div className="port">
                            {service.port}
                          </div>

                          <div className="protocol">
                            {service.protocol.toUpperCase()}
                          </div>

                          <div className="service-name">
                            {service.service}
                          </div>

                          <div className="service-state">
                            <span />

                            {service.state.toUpperCase()}
                          </div>
                        </div>
                      ),
                    )}
                </div>
              </section>

              <section className="panel coverage-panel">
                <div className="panel-header">
                  <div>
                    <span className="panel-kicker">
                      TESTING COVERAGE
                    </span>

                    <h2>
                      Assessment Progress
                    </h2>
                  </div>

                  <div className="coverage-value">
                    {coveragePercent}%
                  </div>
                </div>

                <div className="coverage-ring">
                  <div
                    className="ring"
                    style={{
                      background:
                        `conic-gradient(
                          #d94b4b ${
                            coveragePercent *
                            3.6
                          }deg,
                          #24272c ${
                            coveragePercent *
                            3.6
                          }deg
                        )`,
                    }}
                  >
                    <div className="ring-inner">
                      <strong>
                        {
                          dashboard.testing
                            .tested
                        }
                      </strong>

                      <span>
                        / {coverageTotal}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="coverage-list">
                  {Object.entries(
                    dashboard.testing
                      .coverage,
                  ).map(
                    ([area, tests]) => {
                      const total =
                        Object.keys(
                          tests,
                        ).length;

                      const tested =
                        Object.values(
                          tests,
                        ).filter(
                          (status) =>
                            status ===
                            "tested",
                        ).length;

                      const percentage =
                        total > 0
                          ? Math.round(
                              (tested /
                                total) *
                                100,
                            )
                          : 0;

                      return (
                        <div
                          className="coverage-row"
                          key={area}
                        >
                          <div>
                            <span>
                              {area.toUpperCase()}
                            </span>

                            <small>
                              {tested}/{total} tests
                            </small>
                          </div>

                          <div className="coverage-bar">
                            <span
                              style={{
                                width: `${percentage}%`,
                              }}
                            />
                          </div>

                          <strong>
                            {percentage}%
                          </strong>
                        </div>
                      );
                    },
                  )}
                </div>
              </section>
            </div>

            <div className="bottom-grid">
              <section className="panel findings-panel">
                <div className="panel-header">
                  <div>
                    <span className="panel-kicker">
                      FINDINGS
                    </span>

                    <h2>
                      Security Findings
                    </h2>
                  </div>

                  <button
                    className="panel-action"
                    onClick={() =>
                      navigate("findings")
                    }
                  >
                    OPEN FINDINGS
                    <ChevronRight size={14} />
                  </button>
                </div>

                {findings.length === 0 ? (
                  <div className="empty-state">
                    <Shield size={28} />

                    <strong>
                      No findings recorded
                    </strong>

                    <span>
                      Validated security findings
                      will appear here.
                    </span>
                  </div>
                ) : (
                  <div className="finding-list">
                    {findings.map(
                      (finding) => (
                        <div
                          className="finding-row"
                          key={finding.id}
                        >
                          <div className="severity medium">
                            {finding.severity.toUpperCase()}
                          </div>

                          <div className="finding-main">
                            <strong>
                              {finding.title}
                            </strong>

                            <span>
                              {finding.validation_status.toUpperCase()}
                            </span>
                          </div>

                          <div className="finding-status">
                            <span className="status-check">
                              ✓
                            </span>

                            {finding.status.toUpperCase()}
                          </div>

                          <ChevronRight
                            size={16}
                          />
                        </div>
                      ),
                    )}
                  </div>
                )}
              </section>

              <section className="panel activity-panel">
                <div className="panel-header">
                  <div>
                    <span className="panel-kicker">
                      TELEMETRY
                    </span>

                    <h2>
                      Assessment Activity
                    </h2>
                  </div>

                  <Radio size={17} />
                </div>

                <div className="activity-summary">
                  <div className="activity-number">
                    {dashboard.activities}
                  </div>

                  <div>
                    <strong>
                      Activities recorded
                    </strong>

                    <span>
                      Evidence-backed assessment
                      operations
                    </span>
                  </div>
                </div>

                <div className="activity-line">
                  <div className="activity-marker">
                    <Terminal size={14} />
                  </div>

                  <div>
                    <strong>
                      Tool execution pipeline
                    </strong>

                    <span>
                      Recon → Test → Evidence
                    </span>
                  </div>

                  <small>ACTIVE</small>
                </div>

                <div className="activity-line">
                  <div className="activity-marker">
                    <Wifi size={14} />
                  </div>

                  <div>
                    <strong>
                      Provenance engine
                    </strong>

                    <span>
                      Activity → Evidence → Finding
                    </span>
                  </div>

                  <small>ONLINE</small>
                </div>
              </section>
            </div>
          </section>
        )}

        {view === "attack-surface" && (
          <section className="page attack-surface-page">
            <div className="surface-hero">
              <div>
                <div className="eyebrow">
                  <Network size={12} />

                  ATTACK SURFACE
                </div>

                <h1>
                  Discover & Inspect
                </h1>

                <p>
                  Evidence-backed inventory of
                  discovered assets and exposed
                  services.
                </p>
              </div>

              <div className="surface-metrics">
                <div>
                  <strong>
                    {assets.length
                      .toString()
                      .padStart(2, "0")}
                  </strong>

                  <span>ASSETS</span>
                </div>

                <div>
                  <strong>
                    {services.length
                      .toString()
                      .padStart(2, "0")}
                  </strong>

                  <span>SERVICES</span>
                </div>

                <div>
                  <strong>
                    {
                      services.filter(
                        (service) =>
                          service.state ===
                          "open",
                      ).length
                    }
                  </strong>

                  <span>OPEN</span>
                </div>
              </div>
            </div>

            {surfaceError && (
              <div className="error-banner">
                <AlertTriangle size={16} />

                {surfaceError}
              </div>
            )}

            <div className="surface-toolbar">
              <div className="surface-search">
                <Search size={16} />

                <input
                  value={assetSearch}
                  onChange={(event) =>
                    setAssetSearch(
                      event.target.value,
                    )
                  }
                  placeholder="Search assets, ports, services..."
                />

                {assetSearch && (
                  <button
                    onClick={() =>
                      setAssetSearch("")
                    }
                    aria-label="Clear search"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              <div className="scope-filters">
                {(
                  [
                    ["all", "ALL"],
                    ["include", "IN SCOPE"],
                    ["exclude", "EXCLUDED"],
                    [
                      "unknown",
                      "DISCOVERED",
                    ],
                  ] as const
                ).map(
                  ([value, label]) => (
                    <button
                      key={value}
                      className={
                        scopeFilter === value
                          ? "filter-active"
                          : ""
                      }
                      onClick={() =>
                        setScopeFilter(
                          value,
                        )
                      }
                    >
                      {label}
                    </button>
                  ),
                )}
              </div>
            </div>

            {surfaceLoading ? (
              <div className="surface-loading">
                <div className="loading-pulse" />

                <strong>
                  MAPPING ATTACK SURFACE
                </strong>

                <span>
                  Loading assets, scope and
                  service inventory...
                </span>
              </div>
            ) : (
              <div className="surface-layout">
                <section className="surface-assets panel">
                  <div className="surface-section-header">
                    <div>
                      <span className="panel-kicker">
                        ASSET INVENTORY
                      </span>

                      <h2>
                        Discovered Assets
                      </h2>
                    </div>

                    <span className="result-count">
                      {filteredAssets.length} /{" "}
                      {assets.length}
                    </span>
                  </div>

                  <div className="asset-list">
                    {filteredAssets.length ===
                    0 ? (
                      <div className="empty-surface">
                        <Search size={24} />

                        <strong>
                          No matching assets
                        </strong>

                        <span>
                          Try another search or
                          scope filter.
                        </span>
                      </div>
                    ) : (
                      filteredAssets.map(
                        (asset) => {
                          const scopeType =
                            getScopeType(
                              asset,
                            );

                          const assetServices =
                            getAssetServices(
                              asset.id,
                            );

                          const isSelected =
                            selectedAssetId ===
                            asset.id;

                          return (
                            <button
                              className={`asset-card ${
                                isSelected
                                  ? "asset-selected"
                                  : ""
                              }`}
                              key={asset.id}
                              onClick={() =>
                                setSelectedAssetId(
                                  asset.id,
                                )
                              }
                            >
                              <div className="asset-card-icon">
                                {asset.asset_type ===
                                "domain" ? (
                                  <Globe
                                    size={17}
                                  />
                                ) : (
                                  <Network
                                    size={17}
                                  />
                                )}
                              </div>

                              <div className="asset-card-main">
                                <div className="asset-card-title">
                                  <strong>
                                    {asset.value}
                                  </strong>

                                  <span>
                                    {asset.asset_type.toUpperCase()}
                                  </span>
                                </div>

                                <p>
                                  {asset.description ??
                                    "Discovered asset"}
                                </p>

                                <div className="asset-card-meta">
                                  <span>
                                    {
                                      assetServices.length
                                    }{" "}
                                    service
                                    {assetServices.length ===
                                    1
                                      ? ""
                                      : "s"}
                                  </span>

                                  <span>
                                    {asset.status.toUpperCase()}
                                  </span>
                                </div>
                              </div>

                              <div className="asset-card-right">
                                <ScopeBadge
                                  type={
                                    scopeType
                                  }
                                />

                                <ChevronRight
                                  size={15}
                                />
                              </div>
                            </button>
                          );
                        },
                      )
                    )}
                  </div>
                </section>

                <section className="surface-detail panel">
                  {!selectedAsset ? (
                    <div className="detail-empty">
                      <Network size={32} />

                      <strong>
                        Select an asset
                      </strong>

                      <span>
                        Choose an asset from the
                        inventory to inspect its
                        attack surface.
                      </span>
                    </div>
                  ) : (
                    <>
                      <div className="detail-header">
                        <div className="detail-heading">
                          <button
                            className="mobile-back"
                            onClick={() =>
                              setSelectedAssetId(
                                null,
                              )
                            }
                          >
                            <ArrowLeft
                              size={16}
                            />
                          </button>

                          <div className="detail-icon">
                            <Globe size={20} />
                          </div>

                          <div>
                            <div className="detail-eyebrow">
                              {
                                selectedAsset.asset_type
                              }{" "}
                              / DISCOVERED ASSET
                            </div>

                            <h2>
                              {
                                selectedAsset.value
                              }
                            </h2>
                          </div>
                        </div>

                        <ScopeBadge
                          type={getScopeType(
                            selectedAsset,
                          )}
                        />
                      </div>

                      <div className="detail-description">
                        <span>
                          DESCRIPTION
                        </span>

                        <p>
                          {selectedAsset.description ??
                            "No description recorded."}
                        </p>
                      </div>

                      <div className="detail-divider" />

                      <div className="detail-section">
                        <div className="detail-section-heading">
                          <div>
                            <span className="panel-kicker">
                              ATTACK SURFACE LINKS
                            </span>

                            <h3>
                              Related Assets
                            </h3>
                          </div>

                          <span className="service-total">
                            {selectedRelationships.length}{" "}
                            RELATIONSHIP
                            {selectedRelationships.length === 1
                              ? ""
                              : "S"}
                          </span>
                        </div>

                        {selectedRelationships.length === 0 ? (
                          <div className="no-services">
                            <Network size={20} />

                            <span>
                              No asset relationships have
                              been recorded for this asset.
                            </span>
                          </div>
                        ) : (
                          <div className="detail-services">
                            {selectedRelationships.map(
                              (relationship) => {
                                const isSource =
                                  relationship.source_asset_id ===
                                  selectedAsset.id;

                                const relatedAsset =
                                  getRelationshipAsset(
                                    relationship,
                                    isSource
                                      ? "target"
                                      : "source",
                                  );

                                if (!relatedAsset) {
                                  return null;
                                }

                                return (
                                  <button
                                    className="detail-service"
                                    key={relationship.id}
                                    onClick={() =>
                                      setSelectedAssetId(
                                        relatedAsset.id,
                                      )
                                    }
                                    title={`Inspect ${relatedAsset.value}`}
                                  >
                                    <div className="service-port-large">
                                      <Network size={17} />
                                    </div>

                                    <div className="detail-service-info">
                                      <strong>
                                        {relatedAsset.value}
                                      </strong>

                                      <span>
                                        {isSource
                                          ? "OUTBOUND"
                                          : "INBOUND"}{" "}
                                        /{" "}
                                        {relationship.relationship_type.replaceAll(
                                          "_",
                                          " ",
                                        )}
                                      </span>
                                    </div>

                                    <div className="detail-service-state">
                                      <span />
                                      INSPECT
                                    </div>
                                  </button>
                                );
                              },
                            )}
                          </div>
                        )}
                      </div>

                      <div className="detail-divider" />

                      <div className="detail-section">
                        <div className="detail-section-heading">
                          <div>
                            <span className="panel-kicker">
                              SERVICE INVENTORY
                            </span>

                            <h3>
                              Exposed Services
                            </h3>
                          </div>

                          <span className="service-total">
                            {
                              selectedServices.length
                            }{" "}
                            SERVICES
                          </span>
                        </div>

                        {selectedServices.length ===
                        0 ? (
                          <div className="no-services">
                            <Server
                              size={20}
                            />

                            <span>
                              No services have
                              been discovered for
                              this asset yet.
                            </span>
                          </div>
                        ) : (
                          <div className="detail-services">
                            {selectedServices.map(
                              (
                                service,
                              ) => (
                                <div
                                  className="detail-service"
                                  key={
                                    service.id
                                  }
                                >
                                  <div className="service-port-large">
                                    {
                                      service.port
                                    }
                                  </div>

                                  <div className="detail-service-info">
                                    <strong>
                                      {service.service}
                                    </strong>

                                    <span>
                                      {
                                        service.protocol
                                      }{" "}
                                      / TCP
                                    </span>
                                  </div>

                                  <div className="detail-service-state">
                                    <span />

                                    {service.state.toUpperCase()}
                                  </div>
                                </div>
                              ),
                            )}
                          </div>
                        )}
                      </div>

                      <div className="detail-divider" />

                      <div className="detail-section">
                        <div className="detail-section-heading">
                          <div>
                            <span className="panel-kicker">
                              TESTING SIGNAL
                            </span>

                            <h3>
                              Assessment Coverage
                            </h3>
                          </div>

                          <span className="service-total">
                            {dashboard.testing.tested} / {coverageTotal}
                          </span>
                        </div>

                        <div className="surface-coverage-grid">
                          {Object.entries(
                            dashboard.testing.coverage,
                          ).map(([area, tests]) => {
                            const values = Object.values(tests);
                            const tested = values.filter(
                              (value) => value === "tested",
                            ).length;

                            return (
                              <div
                                className="surface-coverage-card"
                                key={area}
                              >
                                <div className="surface-coverage-top">
                                  <strong>
                                    {area.toUpperCase()}
                                  </strong>
                                  <span>
                                    {tested}/{values.length}
                                  </span>
                                </div>

                                <div className="surface-coverage-bar">
                                  <span
                                    style={{
                                      width: `${
                                        values.length > 0
                                          ? Math.round(
                                              (tested / values.length) *
                                                100,
                                            )
                                          : 0
                                      }%`,
                                    }}
                                  />
                                </div>

                                <div className="surface-coverage-tests">
                                  {Object.entries(tests).map(
                                    ([test, status]) => (
                                      <span key={test}>
                                        <i
                                          className={
                                            status === "tested"
                                              ? "coverage-dot coverage-dot-tested"
                                              : "coverage-dot"
                                          }
                                        />
                                        {test.replaceAll("_", " ")}
                                      </span>
                                    ),
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      <div className="detail-divider" />

                      <div className="detail-section">
                        <div className="detail-section-heading">
                          <div>
                            <span className="panel-kicker">
                              PROVENANCE
                            </span>

                            <h3>
                              Security Records
                            </h3>
                          </div>
                        </div>

                        <div className="surface-record-grid">
                          <div className="surface-record-card">
                            <div className="surface-record-icon">
                              <ShieldCheck size={17} />
                            </div>
                            <div>
                              <strong>
                                {findings.filter(
                                  (finding) =>
                                    finding.asset_id ===
                                    selectedAsset.id,
                                ).length}
                              </strong>
                              <span>FINDINGS</span>
                            </div>
                          </div>

                          <div className="surface-record-card">
                            <div className="surface-record-icon">
                              <FileText size={17} />
                            </div>
                            <div>
                              <strong>
                                {evidence.filter(
                                  (item) =>
                                    item.asset_id ===
                                    selectedAsset.id,
                                ).length}
                              </strong>
                              <span>EVIDENCE ITEMS</span>
                            </div>
                          </div>
                        </div>

                        <div className="surface-provenance-chain">
                          <span>ACTIVITY</span>
                          <ChevronRight size={13} />
                          <span>EVIDENCE</span>
                          <ChevronRight size={13} />
                          <span>FINDING</span>
                          <span className="chain-note">
                            Provenance-backed records
                          </span>
                        </div>
                      </div>

                      <div className="detail-divider" />

                      <div className="detail-section">
                        <div className="detail-section-heading">
                          <div>
                            <span className="panel-kicker">
                              SCOPE DECISION
                            </span>

                            <h3>
                              Authorization Context
                            </h3>
                          </div>
                        </div>

                        <div
                          className={`scope-decision scope-decision-${getScopeType(
                            selectedAsset,
                          )}`}
                        >
                          {getScopeType(
                            selectedAsset,
                          ) ===
                          "include" ? (
                            <Check size={18} />
                          ) : (
                            <AlertTriangle
                              size={18}
                            />
                          )}

                          <div>
                            <strong>
                              {getScopeType(
                                selectedAsset,
                              ) ===
                              "include"
                                ? "Explicitly included in assessment scope"
                                : getScopeType(
                                      selectedAsset,
                                    ) ===
                                    "exclude"
                                  ? "Explicitly excluded from assessment scope"
                                  : "Discovered but not explicitly listed in assessment scope"}
                            </strong>

                            <span>
                              VANTA does not treat
                              discovery as authorization.
                            </span>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </section>
              </div>
            )}
          </section>
        )}


        {view === "testing" && (
          <section className="page testing-page">
            <div className="testing-hero">
              <div>
                <div className="eyebrow">
                  <Terminal size={12} />
                  TEST WORKFLOW
                </div>
                <h1>Plan, Execute & Prove</h1>
                <p>
                  Turn each testing objective into a traceable assessment operation.
                  Select what you are testing, review prior executions, then run an
                  authorized adapter when one is available.
                </p>
              </div>
              <div className="testing-hero-signal">
                <span className="status-dot" />
                SCOPE ENFORCED
              </div>
            </div>

            <div className="testing-workflow-layout">
              <aside className="testing-taxonomy panel">
                <div className="testing-taxonomy-header">
                  <div>
                    <span className="panel-kicker">TESTING TAXONOMY</span>
                    <h2>Assessment Coverage</h2>
                  </div>
                  <span className="testing-taxonomy-count">
                    {coverageTotal} OBJECTIVES
                  </span>
                </div>

                <div className="testing-taxonomy-list">
                  {Object.entries(TESTING_TAXONOMY).map(([area, tests]) => {
                    const areaTested = tests.filter(
                      (test) => dashboard.testing.coverage[area]?.[test] === "tested",
                    ).length;

                    return (
                      <section className="testing-taxonomy-area" key={area}>
                        <div className="testing-taxonomy-area-header">
                          <span>{coverageTestLabel(area)}</span>
                          <small>
                            {areaTested}/{tests.length}
                          </small>
                        </div>

                        <div className="testing-taxonomy-items">
                          {tests.map((test) => {
                            const status =
                              dashboard.testing.coverage[area]?.[test] === "tested"
                                ? "tested"
                                : "untested";
                            const selected =
                              selectedTestingItem.area === area &&
                              selectedTestingItem.test === test;

                            return (
                              <button
                                key={`${area}-${test}`}
                                className={`testing-taxonomy-item ${
                                  selected ? "testing-taxonomy-item-selected" : ""
                                }`}
                                onClick={() => {
                                  setSelectedTestingItem({ area, test });
                                  setTestError(null);
                                  setTestResult(null);
                                }}
                              >
                                <span
                                  className={`testing-status-dot ${
                                    status === "tested"
                                      ? "testing-status-dot-tested"
                                      : ""
                                  }`}
                                >
                                  {status === "tested" ? (
                                    <Check size={10} />
                                  ) : (
                                    <CircleDot size={10} />
                                  )}
                                </span>
                                <span className="testing-taxonomy-item-label">
                                  {coverageTestLabel(test)}
                                </span>
                                {status === "tested" &&
                                  selectedTestingItem.area === area &&
                                  selectedTestingItem.test === test &&
                                  testingTrace && (
                                    <span className="testing-execution-count">
                                      {testingTrace.activity_count}
                                    </span>
                                  )}
                              </button>
                            );
                          })}
                        </div>
                      </section>
                    );
                  })}
                </div>
              </aside>

              <section className="testing-console panel">
                <div className="surface-section-header">
                  <div>
                    <span className="panel-kicker">TEST OBJECTIVE</span>
                    <h2>
                      {coverageTestLabel(selectedTestingItem.area)} / {coverageTestLabel(selectedTestingItem.test)}
                    </h2>
                  </div>
                  <span
                    className={`testing-objective-status ${
                      testingTrace?.status === "tested"
                        ? "testing-objective-status-tested"
                        : ""
                    }`}
                  >
                    {testingTrace?.status === "tested" ? "TESTED" : "NOT TESTED"}
                  </span>
                </div>

                {testingTraceLoading ? (
                  <div className="testing-trace-loading">
                    <div className="loading-pulse" />
                    <strong>LOADING TRACEABILITY</strong>
                    <span>Retrieving executions, evidence and findings...</span>
                  </div>
                ) : testingTraceError ? (
                  <div className="testing-error">
                    <AlertTriangle size={16} />
                    <span>{testingTraceError}</span>
                  </div>
                ) : (
                  <>
                    <div className="testing-trace-summary">
                      <div>
                        <span>EXECUTIONS</span>
                        <strong>{testingTrace?.activity_count ?? 0}</strong>
                      </div>
                      <div>
                        <span>EVIDENCE</span>
                        <strong>
                          {testingTrace?.activities.reduce(
                            (total, activity) => total + activity.evidence.length,
                            0,
                          ) ?? 0}
                        </strong>
                      </div>
                      <div>
                        <span>FINDINGS</span>
                        <strong>
                          {testingTrace?.activities.reduce(
                            (total, activity) =>
                              total +
                              activity.findings.length +
                              activity.evidence.reduce(
                                (evidenceTotal, evidence) =>
                                  evidenceTotal + evidence.findings.length,
                                0,
                              ),
                            0,
                          ) ?? 0}
                        </strong>
                      </div>
                    </div>

                    <div className="testing-objective-copy">
                      {testingTrace?.status === "tested" ? (
                        <p>
                          This objective has recorded executions. VANTA can trace each
                          execution through its evidence and associated findings.
                        </p>
                      ) : (
                        <p>
                          No completed execution is recorded for this testing objective.
                          Select an authorized asset and start a supported test below.
                        </p>
                      )}
                    </div>

                    {testingTrace?.activities[0] && (
                      <div className="testing-latest-execution">
                        <div className="testing-latest-header">
                          <div>
                            <span className="panel-kicker">LATEST EXECUTION</span>
                            <strong>{testingTrace.activities[0].title}</strong>
                          </div>
                          <span>
                            {(testingTrace.activities[0].tool ?? "manual").toUpperCase()}
                          </span>
                        </div>
                        <div className="testing-latest-meta">
                          <span>ACTIVITY <strong>{testingTrace.activities[0].id.slice(0, 8)}</strong></span>
                          <span>EVIDENCE <strong>{testingTrace.activities[0].evidence.length}</strong></span>
                          <span>STATUS <strong>{testingTrace.activities[0].status.toUpperCase()}</strong></span>
                        </div>
                      </div>
                    )}

                    <div className="testing-workflow-actions">
                      <button
                        className="testing-trace-button"
                        onClick={() => {
                          setSelectedCoverageItem(selectedTestingItem);
                          navigate("coverage");
                        }}
                      >
                        <Fingerprint size={16} />
                        VIEW TRACEABILITY
                      </button>

                      {selectedTestingItem.area === EXECUTABLE_TEST.area &&
                      selectedTestingItem.test === EXECUTABLE_TEST.test ? (
                        <span className="testing-adapter-ready">
                          <Radio size={14} />
                          EXECUTION ADAPTER READY
                        </span>
                      ) : (
                        <span className="testing-adapter-pending">
                          <CircleDot size={14} />
                          WORKFLOW ITEM — ADAPTER PENDING
                        </span>
                      )}
                    </div>
                  </>
                )}
              </section>

              <aside className="testing-side panel">
                <span className="panel-kicker">CONTROLLED EXECUTION</span>
                <h2>Run authorized operation</h2>

                <div className="testing-form-grid testing-form-grid-compact">
                  <label className="testing-field testing-field-wide">
                    <span>ASSET</span>
                    <select
                      value={testAssetId ?? ""}
                      onChange={(event) => setTestAssetId(event.target.value)}
                    >
                      {assets.map((asset) => {
                        const scopeType = getScopeType(asset);
                        return (
                          <option
                            key={asset.id}
                            value={asset.id}
                            disabled={scopeType === "exclude"}
                          >
                            {asset.value} — {scopeType.toUpperCase()}
                          </option>
                        );
                      })}
                    </select>
                  </label>

                  <label className="testing-field testing-field-wide">
                    <span>TOOL</span>
                    <select
                      value={testTool}
                      onChange={(event) =>
                        setTestTool(event.target.value as "nmap" | "mock")
                      }
                    >
                      <option value="nmap">Nmap</option>
                      <option value="mock">Mock adapter</option>
                    </select>
                  </label>

                  <div className="testing-field testing-field-wide">
                    <span>TESTING AREA</span>
                    <div className="testing-readonly">
                      {coverageTestLabel(selectedTestingItem.area)}
                    </div>
                  </div>

                  <div className="testing-field testing-field-wide">
                    <span>TEST TYPE</span>
                    <div className="testing-readonly">
                      {coverageTestLabel(selectedTestingItem.test)}
                    </div>
                  </div>

                  <label className="testing-field testing-field-wide">
                    <span>ACTIVITY TITLE</span>
                    <input
                      value={testTitle}
                      onChange={(event) => setTestTitle(event.target.value)}
                      placeholder={coverageTestLabel(selectedTestingItem.test)}
                    />
                  </label>
                </div>

                <div className="testing-authorization">
                  <ShieldCheck size={17} />
                  <div>
                    <strong>Authorization is checked by the backend.</strong>
                    <span>VANTA resolves the selected asset against the engagement scope before the tool executes.</span>
                  </div>
                </div>

                {testError && (
                  <div className="testing-error">
                    <AlertTriangle size={16} />
                    <span>{testError}</span>
                  </div>
                )}

                <button
                  className="testing-execute-button"
                  onClick={executeTest}
                  disabled={
                    testRunning ||
                    !testAssetId ||
                    selectedTestingItem.area !== EXECUTABLE_TEST.area ||
                    selectedTestingItem.test !== EXECUTABLE_TEST.test
                  }
                >
                  <Terminal size={17} />
                  {testRunning ? "EXECUTING TEST..." : "EXECUTE TEST"}
                </button>

                {selectedTestingItem.area !== EXECUTABLE_TEST.area ||
                selectedTestingItem.test !== EXECUTABLE_TEST.test ? (
                  <p className="testing-adapter-note">
                    This workflow objective is already part of VANTA's testing model, but its execution adapter is not connected yet. It cannot be executed as a different test type through the current tool endpoint.
                  </p>
                ) : (
                  <div className="testing-pipeline">
                    {[
                      ["01", "Scope", "Target authorization"],
                      ["02", "Activity", "Tool operation"],
                      ["03", "Evidence", "Raw command output"],
                      ["04", "Inventory", "Discovered services"],
                    ].map(([number, title, detail]) => (
                      <div className="testing-pipeline-step" key={number}>
                        <span>{number}</span>
                        <div>
                          <strong>{title}</strong>
                          <small>{detail}</small>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </aside>
            </div>

            {testResult && (
              <section className="testing-result panel">
                <div className="surface-section-header">
                  <div>
                    <span className="panel-kicker">LATEST EXECUTION</span>
                    <h2>Test recorded successfully</h2>
                  </div>
                  <span className="result-success-badge">RECORDED</span>
                </div>

                <div className="testing-result-grid">
                  <div><span>TOOL</span><strong>{testResult.tool.toUpperCase()}</strong></div>
                  <div><span>TARGET</span><strong>{testResult.target}</strong></div>
                  <div><span>ACTIVITY</span><strong>{testResult.activity_id.slice(0, 8)}</strong></div>
                  <div><span>EVIDENCE</span><strong>{testResult.evidence_id.slice(0, 8)}</strong></div>
                  <div><span>SERVICES DISCOVERED</span><strong>{testResult.discovered_services.length}</strong></div>
                </div>

                {testResult.discovered_services.length > 0 && (
                  <div className="testing-discovered-services">
                    {testResult.discovered_services.map((service) => (
                      <div key={service.id}>
                        <strong>{service.port}</strong>
                        <span>{service.protocol}</span>
                        <span>{service.service}</span>
                        <small>{service.state.toUpperCase()}</small>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}
          </section>
        )}

        {view === "activities" && (
          <section className="page activities-page">
            <div className="activity-hero">
              <div>
                <div className="eyebrow">
                  <Activity size={12} />
                  ASSESSMENT ACTIVITY
                </div>

                <h1>Activity Log</h1>

                <p>
                  Trace every assessment operation from
                  execution to evidence.
                </p>
              </div>

              <div className="activity-hero-metrics">
                <div>
                  <strong>{activities.length.toString().padStart(2, "0")}</strong>
                  <span>ACTIVITIES</span>
                </div>
                <div>
                  <strong>
                    {activities.filter(
                      (activity) =>
                        activity.activity_type ===
                        "tool_execution",
                    ).length
                      .toString()
                      .padStart(2, "0")}
                  </strong>
                  <span>EXECUTIONS</span>
                </div>
                <div>
                  <strong>
                    {activities.filter(
                      (activity) =>
                        activity.activity_type ===
                        "retest",
                    ).length
                      .toString()
                      .padStart(2, "0")}
                  </strong>
                  <span>RETESTS</span>
                </div>
              </div>
            </div>

            {activitiesError && (
              <div className="error-banner">
                <AlertTriangle size={16} />
                {activitiesError}
              </div>
            )}

            {activitiesLoading ? (
              <div className="activities-loading panel">
                <div className="loading-pulse" />
                <strong>LOADING ACTIVITY TELEMETRY</strong>
                <span>
                  Retrieving assessment operations...
                </span>
              </div>
            ) : (
              <div className="activities-workspace">
                <section className="activities-list-panel panel">
                  <div className="activities-toolbar">
                    <div className="activity-search">
                      <Search size={16} />
                      <input
                        value={activitySearch}
                        onChange={(event) =>
                          setActivitySearch(
                            event.target.value,
                          )
                        }
                        placeholder="Search activities, tools, commands..."
                      />
                      {activitySearch && (
                        <button
                          onClick={() =>
                            setActivitySearch("")
                          }
                          aria-label="Clear activity search"
                        >
                          <X size={14} />
                        </button>
                      )}
                    </div>

                    <div className="activity-filters">
                      {(
                        [
                          ["all", "ALL"],
                          ["recon", "RECON"],
                          ["network", "NETWORK"],
                          ["web", "WEB"],
                          ["api", "API"],
                          ["retest", "RETEST"],
                        ] as const
                      ).map(
                        ([value, label]) => (
                          <button
                            key={value}
                            className={
                              activityFilter === value
                                ? "filter-active"
                                : ""
                            }
                            onClick={() =>
                              setActivityFilter(
                                value,
                              )
                            }
                          >
                            {label}
                          </button>
                        ),
                      )}
                    </div>
                  </div>

                  <div className="activity-list-header">
                    <div>
                      <span className="panel-kicker">
                        PROVENANCE STREAM
                      </span>
                      <h2>Assessment Operations</h2>
                    </div>
                    <span className="result-count">
                      {filteredActivities.length} / {activities.length}
                    </span>
                  </div>

                  <div className="activity-record-list">
                    {filteredActivities.length === 0 ? (
                      <div className="activity-empty">
                        <Activity size={25} />
                        <strong>No matching activities</strong>
                        <span>
                          Try another search or activity area.
                        </span>
                      </div>
                    ) : (
                      filteredActivities.map(
                        (activity) => {
                          const area =
                            activityArea(activity);
                          const isSelected =
                            activity.id ===
                            selectedActivityId;

                          return (
                            <button
                              key={activity.id}
                              className={`activity-record ${
                                isSelected
                                  ? "activity-record-selected"
                                  : ""
                              }`}
                              onClick={() =>
                                setSelectedActivityId(
                                  activity.id,
                                )
                              }
                            >
                              <div className="activity-record-marker">
                                {activity.tool ===
                                "nmap" ? (
                                  <Network size={15} />
                                ) : activity.activity_type ===
                                  "retest" ? (
                                  <ShieldCheck
                                    size={15}
                                  />
                                ) : (
                                  <Terminal size={15} />
                                )}
                              </div>

                              <div className="activity-record-main">
                                <div className="activity-record-title">
                                  <strong>
                                    {activity.title}
                                  </strong>
                                  <span
                                    className={`activity-area area-${area}`}
                                  >
                                    {activityAreaLabel(
                                      activity,
                                    )}
                                  </span>
                                </div>

                                <div className="activity-record-meta">
                                  <span>
                                    {activityAssetName(
                                      activity,
                                    )}
                                  </span>
                                  <span>
                                    {activity.tool ??
                                      "INTERNAL"}
                                  </span>
                                  <span>
                                    {activity.status.toUpperCase()}
                                  </span>
                                </div>

                                {activity.command && (
                                  <code>
                                    {activity.command}
                                  </code>
                                )}
                              </div>

                              <div className="activity-record-time">
                                {formatActivityTime(
                                  activity.created_at,
                                )}
                              </div>

                              <ChevronRight size={15} />
                            </button>
                          );
                        },
                      )
                    )}
                  </div>
                </section>

                <aside className="activity-detail panel">
                  {!selectedActivity ? (
                    <div className="activity-detail-empty">
                      <Fingerprint size={31} />
                      <strong>Select an activity</strong>
                      <span>
                        Choose an operation to inspect its
                        provenance and execution details.
                      </span>
                    </div>
                  ) : (
                    <>
                      <div className="activity-detail-header">
                        <div className="activity-detail-icon">
                          {selectedActivity.tool ===
                          "nmap" ? (
                            <Network size={20} />
                          ) : selectedActivity.activity_type ===
                            "retest" ? (
                            <ShieldCheck size={20} />
                          ) : (
                            <Terminal size={20} />
                          )}
                        </div>

                        <div>
                          <div className="detail-eyebrow">
                            {activityAreaLabel(
                              selectedActivity,
                            )}{" "}
                            /{" "}
                            {selectedActivity.activity_type.replace(
                              "_",
                              " ",
                            ).toUpperCase()}
                          </div>
                          <h2>
                            {selectedActivity.title}
                          </h2>
                        </div>
                      </div>

                      <div className="activity-detail-status">
                        <span />
                        {selectedActivity.status.toUpperCase()}
                      </div>

                      <div className="activity-detail-section">
                        <span className="panel-kicker">
                          TARGET ASSET
                        </span>
                        <strong>
                          {activityAssetName(
                            selectedActivity,
                          )}
                        </strong>
                        <small>
                          {selectedActivity.asset_id ??
                            "No asset association"}
                        </small>
                      </div>

                      <div className="activity-detail-section">
                        <span className="panel-kicker">
                          DESCRIPTION
                        </span>
                        <p>
                          {selectedActivity.description ??
                            "No description recorded."}
                        </p>
                      </div>

                      <div className="activity-detail-grid">
                        <div>
                          <span>TOOL</span>
                          <strong>
                            {selectedActivity.tool ??
                              "—"}
                          </strong>
                        </div>

                        <div>
                          <span>AREA</span>
                          <strong>
                            {activityAreaLabel(
                              selectedActivity,
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>RECORDED</span>
                          <strong>
                            {formatActivityTime(
                              selectedActivity.created_at,
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>ACTIVITY ID</span>
                          <strong>
                            {selectedActivity.id}
                          </strong>
                        </div>
                      </div>

                      {selectedActivity.command && (
                        <div className="activity-command">
                          <div className="activity-command-header">
                            <span className="panel-kicker">
                              EXECUTION COMMAND
                            </span>
                            <Terminal size={14} />
                          </div>
                          <code>
                            {selectedActivity.command}
                          </code>
                        </div>
                      )}

                      <div className="provenance-chain">
                        <span className="panel-kicker">
                          PROVENANCE
                        </span>

                        <div className="provenance-step active">
                          <div>
                            <Activity size={14} />
                          </div>
                          <span>ACTIVITY</span>
                          <small>RECORDED</small>
                        </div>

                        <div className="provenance-connector" />

                        <div className="provenance-step">
                          <div>
                            <Fingerprint size={14} />
                          </div>
                          <span>EVIDENCE</span>
                          <small>CAPTURED</small>
                        </div>

                        <div className="provenance-connector" />

                        <div className="provenance-step">
                          <div>
                            <AlertTriangle size={14} />
                          </div>
                          <span>FINDING</span>
                          <small>IF VALIDATED</small>
                        </div>
                      </div>
                    </>
                  )}
                </aside>
              </div>
            )}
          </section>
        )}

        {view === "findings" && (
          <section className="page findings-page">
            <div className="findings-hero">
              <div>
                <div className="eyebrow">
                  <AlertTriangle size={12} />
                  VALIDATED SECURITY FINDINGS
                </div>

                <h1>Findings</h1>

                <p>
                  Findings are linked to assets,
                  activities, evidence, validation,
                  and retesting.
                </p>
              </div>

              <div className="findings-hero-stats">
                <div>
                  <span>TOTAL</span>
                  <strong>{findings.length}</strong>
                </div>
                <div>
                  <span>VALIDATED</span>
                  <strong>
                    {
                      findings.filter(
                        (finding) =>
                          finding.validation_status ===
                          "validated",
                      ).length
                    }
                  </strong>
                </div>
                <div>
                  <span>OPEN</span>
                  <strong>
                    {
                      findings.filter(
                        (finding) =>
                          finding.status === "open",
                      ).length
                    }
                  </strong>
                </div>
                <div>
                  <span>CLOSED</span>
                  <strong>
                    {
                      findings.filter(
                        (finding) =>
                          finding.status === "closed",
                      ).length
                    }
                  </strong>
                </div>
              </div>
            </div>

            {findingsError && (
              <div className="error-banner">
                <AlertTriangle size={16} />
                {findingsError}
              </div>
            )}

            <div className="findings-toolbar panel">
              <div className="findings-search">
                <Search size={14} />
                <input
                  value={findingSearch}
                  onChange={(event) =>
                    setFindingSearch(
                      event.target.value,
                    )
                  }
                  placeholder="Search findings, assets, status..."
                />
              </div>

              <div className="finding-filters">
                {[
                  ["all", "ALL"],
                  ["open", "OPEN"],
                  ["validated", "VALIDATED"],
                  ["unvalidated", "UNVALIDATED"],
                  ["closed", "CLOSED"],
                ].map(([value, label]) => (
                  <button
                    key={value}
                    className={
                      findingFilter === value
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setFindingFilter(
                        value as typeof findingFilter,
                      )
                    }
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {findingsLoading ? (
              <div className="findings-loading panel">
                <div className="loading-pulse" />
                <strong>LOADING FINDINGS</strong>
                <span>
                  Retrieving validated assessment records...
                </span>
              </div>
            ) : (
              <div className="findings-workspace">
                <section className="panel findings-list-panel">
                  <div className="panel-header">
                    <div>
                      <span className="panel-kicker">
                        FINDING REGISTER
                      </span>
                      <h2>
                        {filteredFindings.length}{" "}
                        record
                        {filteredFindings.length === 1
                          ? ""
                          : "s"}
                      </h2>
                    </div>
                  </div>

                  {filteredFindings.length === 0 ? (
                    <div className="finding-empty">
                      <AlertTriangle size={20} />
                      <strong>
                        NO FINDINGS MATCH
                      </strong>
                      <span>
                        Adjust the search or filter to
                        view other assessment records.
                      </span>
                    </div>
                  ) : (
                    <div className="finding-register">
                      {filteredFindings.map(
                        (finding) => {
                          const active =
                            finding.id ===
                            selectedFindingId;

                          return (
                            <button
                              key={finding.id}
                              className={`finding-card ${
                                active
                                  ? "active"
                                  : ""
                              }`}
                              onClick={() =>
                                setSelectedFindingId(
                                  finding.id,
                                )
                              }
                            >
                              <div
                                className={`finding-severity ${findingSeverityClass(
                                  finding.severity,
                                )}`}
                              >
                                {finding.severity.toUpperCase()}
                              </div>

                              <div className="finding-card-main">
                                <strong>
                                  {finding.title}
                                </strong>

                                <span>
                                  {findingAssetName(
                                    finding,
                                  )}
                                  {" · "}
                                  {findingValidationLabel(
                                    finding.validation_status,
                                  )}
                                </span>
                              </div>

                              <div className="finding-card-status">
                                <span
                                  className={
                                    finding.status ===
                                    "closed"
                                      ? "closed"
                                      : "open"
                                  }
                                >
                                  {finding.status.toUpperCase()}
                                </span>
                                <ChevronRight
                                  size={14}
                                />
                              </div>
                            </button>
                          );
                        },
                      )}
                    </div>
                  )}
                </section>

                <aside className="panel finding-detail-panel">
                  {!selectedFinding ? (
                    <div className="finding-detail-empty">
                      <AlertTriangle size={22} />
                      <strong>
                        SELECT A FINDING
                      </strong>
                      <span>
                        Choose a finding from the register
                        to inspect its evidence lineage.
                      </span>
                    </div>
                  ) : (
                    <>
                      <div className="finding-detail-top">
                        <div>
                          <span className="panel-kicker">
                            FINDING DETAIL
                          </span>

                          <h2>
                            {selectedFinding.title}
                          </h2>
                        </div>

                        <div
                          className={`finding-severity large ${findingSeverityClass(
                            selectedFinding.severity,
                          )}`}
                        >
                          {selectedFinding.severity.toUpperCase()}
                        </div>
                      </div>

                      <div className="finding-detail-status">
                        <span
                          className={
                            selectedFinding.status ===
                            "closed"
                              ? "finding-state closed"
                              : "finding-state"
                          }
                        >
                          <span />
                          {selectedFinding.status.toUpperCase()}
                        </span>

                        <span className="validation-state">
                          <Check size={11} />
                          {findingValidationLabel(
                            selectedFinding.validation_status,
                          )}
                        </span>
                      </div>

                      <div className="finding-detail-grid">
                        <div>
                          <span>ASSET</span>
                          <strong>
                            {findingAssetName(
                              selectedFinding,
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>CREATED</span>
                          <strong>
                            {formatFindingDate(
                              selectedFinding.created_at,
                            )}
                          </strong>
                        </div>

                        <div>
                          <span>ACTIVITY</span>
                          <strong>
                            {selectedFinding.activity_id ??
                              "NOT LINKED"}
                          </strong>
                        </div>

                        <div>
                          <span>EVIDENCE</span>
                          <strong>
                            {selectedFinding.evidence_id ??
                              "NOT LINKED"}
                          </strong>
                        </div>
                      </div>

                      <div className="finding-section">
                        <span className="panel-kicker">
                          DESCRIPTION
                        </span>
                        <p>
                          {selectedFinding.description ??
                            "No description recorded."}
                        </p>
                      </div>

                      <div className="finding-section">
                        <span className="panel-kicker">
                          REMEDIATION
                        </span>
                        <p>
                          {selectedFinding.remediation ??
                            "No remediation guidance recorded yet."}
                        </p>
                      </div>

                      <div className="finding-section">
                        <span className="panel-kicker">
                          RETEST
                        </span>

                        <div className="retest-state">
                          <ShieldCheck size={15} />
                          <div>
                            <strong>
                              {selectedFinding.retest_status
                                ? selectedFinding.retest_status.toUpperCase()
                                : "NOT RETESTED"}
                            </strong>
                            <span>
                              {selectedFinding.retest_activity_id
                                ? `Activity ${selectedFinding.retest_activity_id}`
                                : "No retest activity linked"}
                            </span>
                          </div>
                        </div>

                        {selectedFinding.validation_status === "hypothesis" && (
                          <div className="finding-action-panel">
                            <div>
                              <span className="panel-kicker">
                                VALIDATION
                              </span>
                              <p>
                                This finding has not yet been manually validated.
                              </p>
                            </div>
                            <button
                              type="button"
                              className="finding-action-button"
                              disabled={findingActionLoading}
                              onClick={() =>
                                validateFinding(selectedFinding.id)
                              }
                            >
                              <Check size={13} />
                              {findingActionLoading
                                ? "VALIDATING..."
                                : "VALIDATE FINDING"}
                            </button>
                          </div>
                        )}

                        {selectedFinding.validation_status === "validated" &&
                          !selectedFinding.retest_status && (
                            <div className="finding-action-panel">
                              <div>
                                <span className="panel-kicker">
                                  VALIDATED / READY FOR RETEST
                                </span>
                                <p>
                                  Start a retest to verify whether the finding has been remediated.
                                </p>
                              </div>
                              <button
                                type="button"
                                className="finding-action-button"
                                disabled={findingActionLoading}
                                onClick={() =>
                                  startFindingRetest(selectedFinding.id)
                                }
                              >
                                <ShieldCheck size={13} />
                                {findingActionLoading
                                  ? "STARTING..."
                                  : "START RETEST"}
                              </button>
                            </div>
                          )}

                        {selectedFinding.retest_status &&
                          selectedFinding.retest_status.toLowerCase() !== "passed" &&
                          selectedFinding.retest_status.toLowerCase() !== "failed" && (
                            <div className="finding-action-panel">
                              <div>
                                <span className="panel-kicker">
                                  RETEST RESULT
                                </span>
                                <p>
                                  Record the outcome of the latest retest activity.
                                </p>
                              </div>
                              <div className="finding-action-buttons" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                                <button
                                  type="button"
                                  className="finding-action-button"
                                  disabled={findingActionLoading}
                                  onClick={() =>
                                    setFindingRetestResult(
                                      selectedFinding.id,
                                      "passed",
                                    )
                                  }
                                >
                                  <Check size={13} />
                                  {findingActionLoading
                                    ? "SAVING..."
                                    : "PASS RETEST"}
                                </button>
                                <button
                                  type="button"
                                  className="finding-action-button"
                                  disabled={findingActionLoading}
                                  onClick={() =>
                                    setFindingRetestResult(
                                      selectedFinding.id,
                                      "failed",
                                    )
                                  }
                                >
                                  <X size={13} />
                                  {findingActionLoading
                                    ? "SAVING..."
                                    : "FAIL RETEST"}
                                </button>
                              </div>
                            </div>
                          )}

                        {findingActionError && (
                          <span className="finding-action-error">
                            {findingActionError}
                          </span>
                        )}
                      </div>

                      <div className="finding-provenance" style={{ marginTop: 18 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginBottom: 12 }}>
                          <span className="panel-kicker">PROVENANCE CHAIN</span>
                          {findingProvenanceLoading && (
                            <span style={{ fontSize: 11, opacity: 0.6 }}>LOADING...</span>
                          )}
                        </div>

                        {findingProvenanceError && (
                          <div className="error-banner" style={{ marginBottom: 12 }}>
                            <AlertTriangle size={14} />
                            {findingProvenanceError}
                          </div>
                        )}

                        {!findingProvenanceLoading && !findingProvenanceError && findingProvenance && (
                          <>
                            <div className="finding-provenance-chain">
                              <div className={`finding-provenance-step ${findingProvenance.asset ? "active" : ""}`}>
                                <Globe size={14} />
                                <span>ASSET</span>
                                <small>{findingProvenance.asset ? "LINKED" : "MISSING"}</small>
                              </div>

                              <ChevronRight size={14} />

                              <div className={`finding-provenance-step ${findingProvenance.activity ? "active" : ""}`}>
                                <Activity size={14} />
                                <span>ACTIVITY</span>
                                <small>{findingProvenance.activity ? "RECORDED" : "MISSING"}</small>
                              </div>

                              <ChevronRight size={14} />

                              <div className={`finding-provenance-step ${findingProvenance.evidence ? "active" : ""}`}>
                                <Fingerprint size={14} />
                                <span>EVIDENCE</span>
                                <small>{findingProvenance.evidence ? "CAPTURED" : "MISSING"}</small>
                              </div>

                              <ChevronRight size={14} />

                              <div className="finding-provenance-step active">
                                <AlertTriangle size={14} />
                                <span>FINDING</span>
                                <small>RECORDED</small>
                              </div>
                            </div>

                            <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
                              <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10, padding: 12, background: "rgba(255,255,255,0.02)" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7 }}>
                                  <Globe size={14} />
                                  <span className="panel-kicker">ASSET</span>
                                </div>
                                {findingProvenance.asset ? (
                                  <div>
                                    <strong style={{ display: "block", fontSize: 14 }}>{findingProvenance.asset.value}</strong>
                                    <span style={{ display: "block", marginTop: 4, fontSize: 11, opacity: 0.62 }}>
                                      {findingProvenance.asset.asset_type} · {findingProvenance.asset.id}
                                    </span>
                                  </div>
                                ) : (
                                  <span style={{ fontSize: 12, opacity: 0.62 }}>No asset linked to this finding.</span>
                                )}
                              </div>

                              <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10, padding: 12, background: "rgba(255,255,255,0.02)" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7 }}>
                                  <Activity size={14} />
                                  <span className="panel-kicker">ACTIVITY</span>
                                </div>
                                {findingProvenance.activity ? (
                                  <div>
                                    <strong style={{ display: "block", fontSize: 14 }}>{findingProvenance.activity.title}</strong>
                                    <span style={{ display: "block", marginTop: 4, fontSize: 11, opacity: 0.62 }}>
                                      {findingProvenance.activity.testing_area ?? "UNCLASSIFIED"} · {findingProvenance.activity.test_type ?? "UNSPECIFIED"} · {findingProvenance.activity.tool ?? "NO TOOL"}
                                    </span>
                                    {findingProvenance.activity.command && (
                                      <code style={{ display: "block", marginTop: 9, padding: 9, borderRadius: 7, background: "rgba(0,0,0,0.24)", fontSize: 11, overflowX: "auto" }}>
                                        {findingProvenance.activity.command}
                                      </code>
                                    )}
                                    <span style={{ display: "block", marginTop: 7, fontSize: 10, opacity: 0.5 }}>
                                      {findingProvenance.activity.id} · {formatActivityTime(findingProvenance.activity.created_at)}
                                    </span>
                                  </div>
                                ) : (
                                  <span style={{ fontSize: 12, opacity: 0.62 }}>No activity linked to this finding.</span>
                                )}
                              </div>

                              <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10, padding: 12, background: "rgba(255,255,255,0.02)" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7 }}>
                                  <Fingerprint size={14} />
                                  <span className="panel-kicker">EVIDENCE</span>
                                </div>
                                {findingProvenance.evidence ? (
                                  <div>
                                    <strong style={{ display: "block", fontSize: 14 }}>{findingProvenance.evidence.title}</strong>
                                    <span style={{ display: "block", marginTop: 4, fontSize: 11, opacity: 0.62 }}>
                                      {findingProvenance.evidence.evidence_type} · {findingProvenance.evidence.id}
                                    </span>
                                    {findingProvenance.evidence.content && (
                                      <pre style={{ margin: "9px 0 0", padding: 10, borderRadius: 7, background: "rgba(0,0,0,0.24)", fontSize: 11, lineHeight: 1.55, whiteSpace: "pre-wrap", wordBreak: "break-word", maxHeight: 180, overflow: "auto" }}>
                                        {findingProvenance.evidence.content}
                                      </pre>
                                    )}
                                    <span style={{ display: "block", marginTop: 7, fontSize: 10, opacity: 0.5 }}>
                                      {formatEvidenceDate(findingProvenance.evidence.created_at)}
                                    </span>
                                  </div>
                                ) : (
                                  <span style={{ fontSize: 12, opacity: 0.62 }}>No evidence linked to this finding.</span>
                                )}
                              </div>
                            </div>
                          </>
                        )}

                        {!findingProvenanceLoading && !findingProvenanceError && !findingProvenance && (
                          <div style={{ padding: 14, border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10, fontSize: 12, opacity: 0.65 }}>
                            No provenance data available for this finding.
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </aside>
              </div>
            )}
          </section>
        )}

        {view === "coverage" && (
          <section
            className="page"
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 18,
            }}
          >
            <div className="surface-hero">
              <div>
                <div className="eyebrow">
                  <ShieldCheck size={12} />
                  TESTING COVERAGE
                </div>
                <h1>Assessment Coverage</h1>
                <p>
                  Track completed testing and follow each coverage item back to
                  the activities, evidence, and findings that support it.
                </p>
              </div>

              <div className="surface-metrics">
                <div>
                  <strong>{dashboard.testing.tested.toString().padStart(2, "0")}</strong>
                  <span>TESTED</span>
                </div>
                <div>
                  <strong>{dashboard.testing.untested.toString().padStart(2, "0")}</strong>
                  <span>REMAINING</span>
                </div>
                <div>
                  <strong>{coveragePercent}%</strong>
                  <span>OVERALL</span>
                </div>
              </div>
            </div>

            <section className="panel" style={{ padding: 22 }}>
              <div className="panel-header">
                <div>
                  <span className="panel-kicker">ASSESSMENT PROGRESS</span>
                  <h2>Testing Coverage</h2>
                </div>
                <span className="service-total">
                  {dashboard.testing.tested} / {coverageTotal} TESTS
                </span>
              </div>

              <div
                style={{
                  height: 8,
                  background: "#24272c",
                  borderRadius: 999,
                  overflow: "hidden",
                  marginTop: 16,
                }}
              >
                <span
                  style={{
                    display: "block",
                    height: "100%",
                    width: `${coveragePercent}%`,
                    background: "#d94b4b",
                    borderRadius: 999,
                  }}
                />
              </div>
            </section>

            <div className="surface-coverage-grid">
              {Object.entries(dashboard.testing.coverage).map(
                ([area, tests]) => {
                  const entries = Object.entries(tests);
                  const tested = entries.filter(
                    ([, status]) => status === "tested",
                  ).length;
                  const percentage =
                    entries.length > 0
                      ? Math.round((tested / entries.length) * 100)
                      : 0;

                  return (
                    <section
                      className="panel"
                      key={area}
                      style={{ padding: 20 }}
                    >
                      <div className="surface-section-header">
                        <div>
                          <span className="panel-kicker">TESTING AREA</span>
                          <h2>{area.toUpperCase()}</h2>
                        </div>
                        <span className="result-count">
                          {tested} / {entries.length}
                        </span>
                      </div>

                      <div
                        style={{
                          height: 4,
                          background: "#24272c",
                          overflow: "hidden",
                          marginBottom: 14,
                        }}
                      >
                        <span
                          style={{
                            display: "block",
                            height: "100%",
                            width: `${percentage}%`,
                            background: "#b84b4b",
                          }}
                        />
                      </div>

                      <div style={{ display: "grid", gap: 7 }}>
                        {entries.map(([test, status]) => {
                          const isTested = status === "tested";
                          const selected =
                            selectedCoverageItem?.area === area &&
                            selectedCoverageItem?.test === test;

                          return (
                            <button
                              key={test}
                              type="button"
                              onClick={() => {
                                setSelectedCoverageItem({ area, test });
                                setCoverageTrace(null);
                              }}
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 10,
                                width: "100%",
                                padding: "10px 11px",
                                border: selected
                                  ? "1px solid rgba(216,90,90,0.55)"
                                  : "1px solid rgba(255,255,255,0.07)",
                                background: selected
                                  ? "rgba(216,90,90,0.07)"
                                  : "rgba(255,255,255,0.02)",
                                color: "inherit",
                                textAlign: "left",
                                cursor: "pointer",
                              }}
                            >
                              <span
                                style={{
                                  width: 7,
                                  height: 7,
                                  flex: "0 0 auto",
                                  borderRadius: "50%",
                                  background: isTested ? "#6fba8b" : "#4d535a",
                                }}
                              />
                              <span style={{ flex: 1, fontSize: 11 }}>
                                {coverageTestLabel(test)}
                              </span>
                              <span
                                style={{
                                  fontFamily: '"JetBrains Mono", monospace',
                                  fontSize: 8,
                                  color: isTested ? "#6fba8b" : "#656b73",
                                }}
                              >
                                {isTested ? "TESTED" : "UNTESTED"}
                              </span>
                              <ChevronRight size={13} />
                            </button>
                          );
                        })}
                      </div>
                    </section>
                  );
                },
              )}
            </div>

            {selectedCoverageItem && (
              <section className="panel" style={{ padding: 22 }}>
                <div className="surface-section-header">
                  <div>
                    <span className="panel-kicker">TRACEABILITY</span>
                    <h2>
                      {coverageTestLabel(selectedCoverageItem.area)} / {coverageTestLabel(selectedCoverageItem.test)}
                    </h2>
                  </div>
                  {coverageTrace && (
                    <span
                      className={`scope-badge ${
                        coverageTrace.status === "tested"
                          ? "scope-in"
                          : "scope-unknown"
                      }`}
                    >
                      <span />
                      {coverageTrace.status.toUpperCase()}
                    </span>
                  )}
                </div>

                {coverageTraceLoading ? (
                  <div className="surface-loading" style={{ marginTop: 16 }}>
                    <div className="loading-pulse" />
                    <strong>LOADING TRACEABILITY</strong>
                    <span>Following activity → evidence → finding provenance...</span>
                  </div>
                ) : coverageTraceError ? (
                  <div className="error-banner" style={{ marginTop: 16 }}>
                    <AlertTriangle size={16} />
                    {coverageTraceError}
                  </div>
                ) : !coverageTrace ? (
                  <div className="detail-empty" style={{ minHeight: 140, marginTop: 16 }}>
                    <ShieldCheck size={28} />
                    <strong>Select a coverage item</strong>
                    <span>Choose a testing item above to inspect its provenance.</span>
                  </div>
                ) : coverageTrace.activities.length === 0 ? (
                  <div className="detail-empty" style={{ minHeight: 140, marginTop: 16 }}>
                    <CircleDot size={28} />
                    <strong>Coverage not tested</strong>
                    <span>No completed activity has been recorded for this testing item.</span>
                  </div>
                ) : (
                  <div style={{ display: "grid", gap: 12, marginTop: 16 }}>
                    {coverageTrace.activities.map((activity) => (
                      <article
                        key={activity.id}
                        style={{
                          border: "1px solid rgba(255,255,255,0.08)",
                          borderRadius: 10,
                          padding: 15,
                          background: "rgba(255,255,255,0.018)",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 14 }}>
                          <div style={{ minWidth: 0 }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                              <Activity size={14} />
                              <strong style={{ fontSize: 13 }}>{activity.title}</strong>
                            </div>
                            <div style={{ marginTop: 6, fontSize: 10, opacity: 0.58 }}>
                              {activity.tool ?? "NO TOOL"} · {activity.status.toUpperCase()} · {formatActivityTime(activity.created_at)}
                            </div>
                          </div>
                          <span style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 8, opacity: 0.45 }}>
                            {activity.id}
                          </span>
                        </div>

                        {activity.command && (
                          <code
                            style={{
                              display: "block",
                              marginTop: 11,
                              padding: 10,
                              borderRadius: 7,
                              background: "#0b0d0f",
                              color: "#aeb4bb",
                              fontFamily: '"JetBrains Mono", monospace',
                              fontSize: 9,
                              overflowX: "auto",
                            }}
                          >
                            {activity.command}
                          </code>
                        )}

                        <div className="finding-provenance-chain" style={{ marginTop: 14 }}>
                          <div className="finding-provenance-step active">
                            <Activity size={13} />
                            <span>ACTIVITY</span>
                            <small>RECORDED</small>
                          </div>
                          <ChevronRight size={13} />
                          <div className={`finding-provenance-step ${activity.evidence.length > 0 ? "active" : ""}`}>
                            <Fingerprint size={13} />
                            <span>EVIDENCE</span>
                            <small>{activity.evidence.length} CAPTURED</small>
                          </div>
                          <ChevronRight size={13} />
                          <div className={`finding-provenance-step ${activity.findings.length > 0 ? "active" : ""}`}>
                            <AlertTriangle size={13} />
                            <span>FINDING</span>
                            <small>{activity.findings.length} LINKED</small>
                          </div>
                        </div>

                        {activity.evidence.map((item) => (
                          <div
                            key={item.id}
                            style={{
                              marginTop: 13,
                              padding: 12,
                              border: "1px solid rgba(255,255,255,0.07)",
                              borderRadius: 8,
                            }}
                          >
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                              <Fingerprint size={13} />
                              <strong style={{ fontSize: 11 }}>{item.title}</strong>
                              <span style={{ fontSize: 8, opacity: 0.5 }}>{item.evidence_type.toUpperCase()}</span>
                            </div>

                            {item.content && (
                              <pre
                                style={{
                                  margin: "10px 0 0",
                                  padding: 10,
                                  maxHeight: 180,
                                  overflow: "auto",
                                  background: "#0b0d0f",
                                  color: "#aeb4bb",
                                  fontFamily: '"JetBrains Mono", monospace',
                                  fontSize: 9,
                                  lineHeight: 1.55,
                                  whiteSpace: "pre-wrap",
                                  wordBreak: "break-word",
                                }}
                              >
                                {item.content}
                              </pre>
                            )}

                            {item.findings.length > 0 ? (
                              <div style={{ display: "grid", gap: 7, marginTop: 10 }}>
                                {item.findings.map((finding) => (
                                  <div
                                    key={finding.id}
                                    style={{
                                      display: "flex",
                                      alignItems: "center",
                                      gap: 9,
                                      padding: "8px 9px",
                                      border: "1px solid rgba(216,90,90,0.2)",
                                      background: "rgba(216,90,90,0.05)",
                                    }}
                                  >
                                    <AlertTriangle size={13} />
                                    <span style={{ flex: 1, fontSize: 10 }}>{finding.title}</span>
                                    <span style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 8 }}>
                                      {finding.severity.toUpperCase()}
                                    </span>
                                    <span style={{ fontSize: 8, opacity: 0.6 }}>
                                      {finding.validation_status.toUpperCase()}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div style={{ marginTop: 9, fontSize: 9, opacity: 0.5 }}>
                                No finding linked to this evidence. Testing is still recorded as completed.
                              </div>
                            )}
                          </div>
                        ))}
                      </article>
                    ))}
                  </div>
                )}
              </section>
            )}
          </section>
        )}

        {view === "evidence" && (
          <section className="page" style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            <div className="surface-hero">
              <div>
                <div className="eyebrow">
                  <Fingerprint size={12} />
                  EVIDENCE WORKSPACE
                </div>
                <h1>Assessment Evidence</h1>
                <p>
                  Inspect captured artifacts and trace each item back to the assessment activity that produced it.
                </p>
              </div>

              <div className="surface-metrics">
                <div>
                  <strong>{evidence.length.toString().padStart(2, "0")}</strong>
                  <span>EVIDENCE</span>
                </div>
                <div>
                  <strong>{evidence.filter((item) => item.evidence_type === "command_output").length.toString().padStart(2, "0")}</strong>
                  <span>COMMAND OUTPUT</span>
                </div>
                <div>
                  <strong>{evidence.filter((item) => item.evidence_type === "retest").length.toString().padStart(2, "0")}</strong>
                  <span>RETEST</span>
                </div>
              </div>
            </div>

            {evidenceError && (
              <div className="error-banner">
                <AlertTriangle size={16} />
                {evidenceError}
              </div>
            )}

            {evidenceLoading ? (
              <div className="surface-loading">
                <div className="loading-pulse" />
                <strong>LOADING EVIDENCE</strong>
                <span>Retrieving captured assessment artifacts...</span>
              </div>
            ) : (
              <>
                <div className="surface-toolbar">
                  <div className="surface-search">
                    <Search size={16} />
                    <input
                      value={evidenceSearch}
                      onChange={(event) => setEvidenceSearch(event.target.value)}
                      placeholder="Search evidence, assets, activity IDs..."
                    />
                    {evidenceSearch && (
                      <button onClick={() => setEvidenceSearch("")} aria-label="Clear evidence search">
                        <X size={14} />
                      </button>
                    )}
                  </div>

                  <div className="scope-filters">
                    {[
                      ["all", "ALL"],
                      ["command_output", "COMMAND OUTPUT"],
                      ["retest", "RETEST"],
                    ].map(([value, label]) => (
                      <button
                        key={value}
                        className={evidenceFilter === value ? "filter-active" : ""}
                        onClick={() => setEvidenceFilter(value as typeof evidenceFilter)}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="surface-layout">
                  <section className="surface-assets panel">
                    <div className="surface-section-header">
                      <div>
                        <span className="panel-kicker">EVIDENCE REGISTER</span>
                        <h2>Captured Artifacts</h2>
                      </div>
                      <span className="result-count">
                        {filteredEvidence.length} / {evidence.length}
                      </span>
                    </div>

                    <div className="asset-list">
                      {filteredEvidence.length === 0 ? (
                        <div className="empty-surface">
                          <Fingerprint size={24} />
                          <strong>NO MATCHING EVIDENCE</strong>
                          <span>Try another search or evidence filter.</span>
                        </div>
                      ) : (
                        filteredEvidence.map((item) => {
                          const active = item.id === selectedEvidenceId;
                          return (
                            <button
                              key={item.id}
                              className={`asset-card ${active ? "asset-selected" : ""}`}
                              onClick={() => setSelectedEvidenceId(item.id)}
                            >
                              <div className="asset-card-icon">
                                {item.evidence_type === "retest" ? (
                                  <ShieldCheck size={17} />
                                ) : (
                                  <Terminal size={17} />
                                )}
                              </div>
                              <div className="asset-card-main">
                                <div className="asset-card-title">
                                  <strong>{item.title}</strong>
                                  <span>{item.evidence_type.toUpperCase()}</span>
                                </div>
                                <p>
                                  {item.content.length > 120
                                    ? `${item.content.slice(0, 120)}...`
                                    : item.content}
                                </p>
                                <div className="asset-card-meta">
                                  <span>{evidenceAssetName(item)}</span>
                                  <span>{formatEvidenceDate(item.created_at)}</span>
                                </div>
                              </div>
                              <div className="asset-card-right">
                                <span className="scope-badge scope-unknown">
                                  <span />
                                  CAPTURED
                                </span>
                                <ChevronRight size={15} />
                              </div>
                            </button>
                          );
                        })
                      )}
                    </div>
                  </section>

                  <section className="surface-detail panel">
                    {!selectedEvidence ? (
                      <div className="detail-empty">
                        <Fingerprint size={32} />
                        <strong>Select evidence</strong>
                        <span>Choose an artifact from the register to inspect its provenance and content.</span>
                      </div>
                    ) : (
                      <>
                        <div className="detail-header">
                          <div className="detail-heading">
                            <div className="detail-icon">
                              {selectedEvidence.evidence_type === "retest" ? (
                                <ShieldCheck size={20} />
                              ) : (
                                <Terminal size={20} />
                              )}
                            </div>
                            <div>
                              <div className="detail-eyebrow">
                                {selectedEvidence.evidence_type} / CAPTURED ARTIFACT
                              </div>
                              <h2>{selectedEvidence.title}</h2>
                            </div>
                          </div>
                          <span className="scope-badge scope-unknown">
                            <span />
                            {selectedEvidence.evidence_type.toUpperCase()}
                          </span>
                        </div>

                        <div className="detail-description">
                          <span>CAPTURE CONTEXT</span>
                          <p>{evidenceAssetName(selectedEvidence)}</p>
                        </div>

                        <div className="detail-divider" />

                        <div className="detail-section">
                          <div className="detail-section-heading">
                            <div>
                              <span className="panel-kicker">ARTIFACT CONTENT</span>
                              <h3>Evidence</h3>
                            </div>
                            <span className="service-total">{selectedEvidence.content.length} CHARS</span>
                          </div>

                          <pre style={{ margin: 0, padding: 14, overflow: "auto", maxHeight: 430, border: "1px solid #24272c", background: "#0b0d0f", color: "#aeb4bb", fontFamily: '"JetBrains Mono", monospace', fontSize: 9, lineHeight: 1.65, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                            {selectedEvidence.content}
                          </pre>
                        </div>

                        <div className="detail-divider" />

                        <div className="detail-section">
                          <span className="panel-kicker">PROVENANCE</span>
                          <div className="finding-provenance-chain" style={{ marginTop: 12 }}>
                            <div className="finding-provenance-step active">
                              <Activity size={14} />
                              <span>ACTIVITY</span>
                              <small>{selectedEvidence.activity_id ? "LINKED" : "MISSING"}</small>
                            </div>
                            <ChevronRight size={14} />
                            <div className="finding-provenance-step active">
                              <Fingerprint size={14} />
                              <span>EVIDENCE</span>
                              <small>CAPTURED</small>
                            </div>
                            <ChevronRight size={14} />
                            <div className="finding-provenance-step">
                              <AlertTriangle size={14} />
                              <span>FINDING</span>
                              <small>IF LINKED</small>
                            </div>
                          </div>
                        </div>

                        <div className="finding-detail-grid" style={{ marginTop: 18 }}>
                          <div>
                            <span>ACTIVITY ID</span>
                            <strong>{selectedEvidence.activity_id ?? "NOT LINKED"}</strong>
                          </div>
                          <div>
                            <span>ASSET</span>
                            <strong>{evidenceAssetName(selectedEvidence)}</strong>
                          </div>
                          <div>
                            <span>CREATED</span>
                            <strong>{formatEvidenceDate(selectedEvidence.created_at)}</strong>
                          </div>
                          <div>
                            <span>FILE</span>
                            <strong>{selectedEvidence.file_path ?? "INLINE ARTIFACT"}</strong>
                          </div>
                        </div>
                      </>
                    )}
                  </section>
                </div>
              </>
            )}
          </section>
        )}


      </main>
    </div>
  );
}

export default App;