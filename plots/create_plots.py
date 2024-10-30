import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

def create_plots(policy_report):
    sns.set_theme(style="whitegrid")

    if 'sdg5_alignment' in policy_report and 'breakdown' in policy_report['sdg5_alignment']:
        breakdown = policy_report['sdg5_alignment']['breakdown']
        if breakdown:
            breakdown_df = pd.DataFrame(breakdown)
            
            # Create a dictionary for short names
            short_names = {
                "5.1": "End discrimination",
                "5.2": "Eliminate violence",
                "5.3": "Eliminate harmful practices",
                "5.4": "Value unpaid care",
                "5.5": "Ensure participation",
                "5.6": "Ensure health rights",
                "5.A": "Equal economic rights",
                "5.B": "Enhance technology use",
                "5.C": "Strengthen policies"
            }
            
            # Add short names to the dataframe
            breakdown_df['short_target'] = breakdown_df['target'].apply(lambda x: short_names[x.split(' - ')[0]])
            
            # Sort the dataframe by score in descending order
            breakdown_df = breakdown_df.sort_values('score', ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create the barplot using short names
            barplot = sns.barplot(x="score", y="short_target", data=breakdown_df, ax=ax, 
                                  palette="viridis")
            
            ax.set_title("Goal 5 Alignment", fontsize=16, fontweight='bold')
            ax.set_xlabel("Score", fontsize=12)
            ax.set_ylabel("Target", fontsize=12)
            
            # Increase font size of tick labels
            ax.tick_params(axis='both', which='major', labelsize=10)
            
            # Add value annotations to the end of each bar
            for p in barplot.patches:
                ax.annotate(f'{p.get_width():.1f}', 
                            (p.get_width(), p.get_y() + p.get_height() / 2),
                            ha='left', va='center',
                            xytext=(5, 0), textcoords='offset points',
                            fontsize=10, fontweight='bold')
            
            # Adjust layout and save
            plt.tight_layout()
            fig = fig_to_base64(fig)
            return fig

def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=300)
    img.seek(0)
    new_fig = base64.b64encode(img.getvalue())
    html = '<img src="data:image/png;base64,{}">'.format(new_fig.decode('utf-8'))
    return html