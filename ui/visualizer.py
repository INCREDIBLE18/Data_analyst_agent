"""
Visualization module.

Auto-generates appropriate charts based on query results.
"""

from typing import Optional, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


class DataVisualizer:
    """Handles automatic chart generation based on data characteristics."""
    
    def __init__(self):
        """Initialize visualizer."""
        pass
    
    def create_visualization(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Automatically create appropriate visualization based on data.
        
        Args:
            df: DataFrame with query results
            
        Returns:
            Plotly figure or None if visualization not suitable
        """
        if df.empty or len(df) == 0:
            return None
        
        # Determine visualization type based on data characteristics
        viz_type = self._determine_viz_type(df)
        
        if viz_type == "time_series":
            return self._create_time_series_chart(df)
        elif viz_type == "bar":
            return self._create_bar_chart(df)
        elif viz_type == "pie":
            return self._create_pie_chart(df)
        elif viz_type == "scatter":
            return self._create_scatter_chart(df)
        else:
            return None
    
    def _determine_viz_type(self, df: pd.DataFrame) -> str:
        """
        Determine the most appropriate visualization type.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Visualization type string
        """
        if len(df.columns) < 2:
            return "none"
        
        # Check for date/time columns
        date_col = self._find_date_column(df)
        
        if date_col is not None:
            return "time_series"
        
        # Check for categorical + numeric pattern
        categorical_cols = self._get_categorical_columns(df)
        numeric_cols = self._get_numeric_columns(df)
        
        # Filter out ID columns from categorical for better visualization
        non_id_categorical = [col for col in categorical_cols if 'id' not in col.lower()]
        non_id_numeric = [col for col in numeric_cols if 'id' not in col.lower()]
        
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # If one categorical and one numeric, good for bar chart
            if len(categorical_cols) == 1 and len(numeric_cols) == 1:
                # If few categories, could be pie chart
                if len(df) <= 10 and df[categorical_cols[0]].nunique() <= 10:
                    return "pie"
                return "bar"
            
            # Multiple numeric columns - if there's an ID column, use bar chart
            if len(categorical_cols) == 1 or len(non_id_numeric) >= 2:
                return "bar"
        
        # Two numeric columns (excluding IDs) - scatter plot
        if len(non_id_numeric) >= 2 and len(df) <= 1000:
            return "scatter"
        
        # Only numeric columns - scatter if 2+ columns, otherwise show message
        if len(numeric_cols) >= 2 and len(categorical_cols) == 0:
            if len(df) <= 1000:
                return "scatter"
        
        # Single column or all IDs - no good visualization
        if len(non_id_numeric) == 0 and len(non_id_categorical) == 0:
            return "none"
        
        return "bar"  # Default to bar chart
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Find a column that contains date/time data.
        
        Args:
            df: DataFrame to search
            
        Returns:
            Column name or None
        """
        import warnings
        
        for col in df.columns:
            # Check if column name suggests a date
            col_lower = col.lower()
            if any(word in col_lower for word in ['date', 'time', 'month', 'year', 'day', 'timestamp']):
                # Verify it's actually a date
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        parsed = pd.to_datetime(df[col].head(), errors='coerce')
                        if parsed.notna().sum() > len(df[col].head()) * 0.5:
                            return col
                except:
                    continue
        
        return None
    
    def _get_categorical_columns(self, df: pd.DataFrame) -> list:
        """Get list of categorical columns."""
        categorical = []
        for col in df.columns:
            col_lower = col.lower()
            nunique = df[col].nunique()
            
            # String/object columns are categorical
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                categorical.append(col)
            # ID columns (even if numeric) should be treated as categorical for visualization
            elif 'id' in col_lower and nunique > 10:
                categorical.append(col)
            # Columns with few unique values are categorical
            elif nunique <= 20:
                categorical.append(col)
            # Columns with less than 50% unique values
            elif nunique < len(df) * 0.5:
                categorical.append(col)
        return categorical
    
    def _get_numeric_columns(self, df: pd.DataFrame) -> list:
        """Get list of numeric columns."""
        return df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    
    def _create_time_series_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create an enhanced time series line chart with area fill."""
        date_col = self._find_date_column(df)
        numeric_cols = self._get_numeric_columns(df)
        
        if not date_col or not numeric_cols:
            return self._create_bar_chart(df)
        
        # Convert date column to datetime
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        df_copy = df_copy.sort_values(date_col)
        
        # Create line chart with area fill
        fig = go.Figure()
        
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']
        
        for idx, col in enumerate(numeric_cols[:3]):  # Limit to 3 lines
            fig.add_trace(go.Scatter(
                x=df_copy[date_col],
                y=df_copy[col],
                mode='lines+markers',
                name=col.replace('_', ' ').title(),
                line=dict(width=3, color=colors[idx % len(colors)]),
                marker=dict(size=8, line=dict(width=2, color='white')),
                fill='tonexty' if idx > 0 else 'tozeroy',
                fillcolor=f'rgba({int(colors[idx % len(colors)][1:3], 16)}, {int(colors[idx % len(colors)][3:5], 16)}, {int(colors[idx % len(colors)][5:7], 16)}, 0.2)',
                hovertemplate='<b>%{x}</b><br>%{y:,.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(
                text=f"Trends Over Time",
                font=dict(size=20, color='#333')
            ),
            xaxis_title=date_col.replace('_', ' ').title(),
            yaxis_title="Value",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def _create_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create an enhanced bar chart with gradients."""
        categorical_cols = self._get_categorical_columns(df)
        numeric_cols = self._get_numeric_columns(df)
        
        if not categorical_cols or not numeric_cols:
            return None
        
        # Prefer non-ID columns for x-axis
        non_id_categorical = [col for col in categorical_cols if 'id' not in col.lower()]
        x_col = non_id_categorical[0] if non_id_categorical else categorical_cols[0]
        
        # Prefer non-ID numeric columns for y-axis
        non_id_numeric = [col for col in numeric_cols if 'id' not in col.lower()]
        y_col = non_id_numeric[0] if non_id_numeric else numeric_cols[0]
        
        # Limit to top 15 categories for readability
        # If there are too many unique categories (like Student IDs), aggregate
        if df[x_col].nunique() > 50:
            # Show top 15 by y_col value
            df_plot = df.nlargest(15, y_col).copy()
        elif len(df) > 15:
            df_plot = df.nlargest(15, y_col).copy()
        else:
            df_plot = df.copy()
        
        df_plot = df_plot.sort_values(y_col, ascending=False)
        
        # Create gradient colors based on values
        colors = df_plot[y_col].values
        
        fig = go.Figure(data=[
            go.Bar(
                x=df_plot[x_col],
                y=df_plot[y_col],
                marker=dict(
                    color=colors,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title=y_col)
                ),
                text=df_plot[y_col].apply(lambda x: f'{x:,.0f}'),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>%{y:,.2f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(
                text=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                font=dict(size=20, color='#333')
            ),
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            template='plotly_white',
            height=500,
            showlegend=False,
            hovermode='x'
        )
        
        # Rotate x-axis labels if many categories
        if len(df_plot) > 5:
            fig.update_xaxes(tickangle=-45)
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create an enhanced donut chart with percentages."""
        categorical_cols = self._get_categorical_columns(df)
        numeric_cols = self._get_numeric_columns(df)
        
        if not categorical_cols or not numeric_cols:
            return None
        
        labels_col = categorical_cols[0]
        values_col = numeric_cols[0]
        
        fig = go.Figure(data=[go.Pie(
            labels=df[labels_col],
            values=df[values_col],
            hole=0.4,
            marker=dict(
                colors=px.colors.qualitative.Set3,
                line=dict(color='white', width=2)
            ),
            textposition='auto',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Value: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(
                text=f"{values_col.replace('_', ' ').title()} Distribution",
                font=dict(size=20, color='#333')
            ),
            template='plotly_white',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create a scatter plot."""
        numeric_cols = self._get_numeric_columns(df)
        
        if len(numeric_cols) < 2:
            return self._create_bar_chart(df)
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        # Sample data if too large
        df_plot = df.sample(n=min(500, len(df)), random_state=42) if len(df) > 500 else df
        
        fig = px.scatter(
            df_plot,
            x=x_col,
            y=y_col,
            title=f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}" + (f" (showing {len(df_plot)} of {len(df)} points)" if len(df_plot) < len(df) else ""),
            template='plotly_white',
            height=500,
            trendline="ols" if len(df_plot) <= 200 else None,
            labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()}
        )
        
        fig.update_traces(
            marker=dict(
                size=6,
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            hovertemplate=f'<b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y}}<extra></extra>'
        )
        
        fig.update_layout(
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray')
        )
        
        return fig
    
    def create_heatmap(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create correlation heatmap for numeric columns."""
        numeric_cols = self._get_numeric_columns(df)
        
        if len(numeric_cols) < 2:
            return None
        
        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title="Correlation Heatmap",
            template='plotly_white',
            height=500,
            width=600
        )
        
        return fig
    
    def create_box_plot(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create box plot for distribution analysis."""
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        
        if not numeric_cols:
            return None
        
        if categorical_cols:
            # Box plot by category
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            
            fig = go.Figure()
            for category in df[x_col].unique():
                fig.add_trace(go.Box(
                    y=df[df[x_col] == category][y_col],
                    name=str(category),
                    marker_color=px.colors.qualitative.Plotly[len(fig.data) % len(px.colors.qualitative.Plotly)]
                ))
            
            fig.update_layout(
                title=f"{y_col.replace('_', ' ').title()} Distribution by {x_col.replace('_', ' ').title()}",
                yaxis_title=y_col.replace('_', ' ').title(),
                template='plotly_white',
                height=500,
                showlegend=True
            )
        else:
            # Single box plot
            fig = go.Figure()
            for col in numeric_cols[:4]:  # Limit to 4 columns
                fig.add_trace(go.Box(
                    y=df[col],
                    name=col.replace('_', ' ').title(),
                    marker_color=px.colors.qualitative.Plotly[len(fig.data) % len(px.colors.qualitative.Plotly)]
                ))
            
            fig.update_layout(
                title="Distribution Analysis",
                template='plotly_white',
                height=500,
                showlegend=True
            )
        
        return fig
    
    def create_funnel_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create funnel chart for conversion analysis."""
        if len(df) < 2:
            return None
        
        categorical_cols = self._get_categorical_columns(df)
        numeric_cols = self._get_numeric_columns(df)
        
        if not categorical_cols or not numeric_cols:
            return None
        
        stage_col = categorical_cols[0]
        value_col = numeric_cols[0]
        
        fig = go.Figure(go.Funnel(
            y=df[stage_col],
            x=df[value_col],
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(
                color=px.colors.sequential.Blues_r[:len(df)]
            )
        ))
        
        fig.update_layout(
            title=f"Conversion Funnel: {value_col.replace('_', ' ').title()}",
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_gauge_chart(self, value: float, title: str, max_value: float = 100.0) -> go.Figure:
        """Create gauge chart for KPI display."""
        if max_value is None:
            max_value = value * 1.5
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 20}},
            gauge={
                'axis': {'range': [None, max_value], 'tickwidth': 1},
                'bar': {'color': "#667eea"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, max_value * 0.3], 'color': '#fee'},
                    {'range': [max_value * 0.3, max_value * 0.7], 'color': '#ffe'},
                    {'range': [max_value * 0.7, max_value], 'color': '#efe'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    
    def create_metric_cards(self, df: pd.DataFrame) -> dict:
        """
        Create summary metrics from data.
        
        Args:
            df: DataFrame with query results
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        numeric_cols = self._get_numeric_columns(df)
        
        for col in numeric_cols:
            metrics[col] = {
                "sum": df[col].sum(),
                "mean": df[col].mean(),
                "max": df[col].max(),
                "min": df[col].min(),
                "count": len(df)
            }
        
        return metrics
