{{/*
Расширяем имя чарта
*/}}
{{- define "diabetes-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Создаем полное имя приложения
*/}}
{{- define "diabetes-service.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Создаем метки чарта
*/}}
{{- define "diabetes-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Общие метки
*/}}
{{- define "diabetes-service.labels" -}}
helm.sh/chart: {{ include "diabetes-service.chart" . }}
{{ include "diabetes-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- range $key, $value := .Values.labels }}
{{ $key }}: {{ $value | quote }}
{{- end }}
{{- end }}

{{/*
Selector метки
*/}}
{{- define "diabetes-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "diabetes-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Создаем имя сервис аккаунта
*/}}
{{- define "diabetes-service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "diabetes-service.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}