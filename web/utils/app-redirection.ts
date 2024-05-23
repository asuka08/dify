export const getRedirection = (
  isCurrentWorkspaceManager: boolean,
  app: any,
  redirectionFunc: (href: string) => void,
) => {
  if (app.mode === 'workflow' || app.mode === 'advanced-chat')
    redirectionFunc(`/app/${app.id}/workflow`)
  else
    redirectionFunc(`/app/${app.id}/configuration`)
}
