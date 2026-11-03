# Get Your Machine Ready

Use Astrona, kubectl, kind, Podman, Python 3, curl and a shell for the practical exercises. Cilium exercises also use Helm and the Hubble CLI. Keep enough memory available for controllers and a private two-node cluster; Events uses a three-member internal event bus. The runtime downloads pinned container images and, where needed, checksum-verified controller manifests or charts.

Launch the module playground from the reading interface. A graded task launches its own environment and does not share state with the playground. Export only the kubeconfig returned for that environment, then check its context before running commands. The task and solution provide the exact private context name. Keep your personal cluster connection separate.

Work through the reading, attempt each task, then inspect the solution. The guided practice before the summary uses the ungraded playground. Record the actual observation before removing the environment. Cleanup markers end playground sessions; use the destroy command in each solution for its independent lab.

These disposable fixtures do not require cloud accounts or external Git writes. Larger production features have prerequisites and limits stated in the individual exercise. Static checks verify content and scripts; they do not establish a completed cluster run.
