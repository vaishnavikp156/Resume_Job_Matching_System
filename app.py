                    f"{job['text_similarity'] * 100:.2f}%"

                )



            with score_col2:



                st.write(

                    f"**Skill Match:** "

                    f"{job['skill_score'] * 100:.2f}%"

                )





            # ==================================

            # MATCHED SKILLS

            # ==================================



            if matched_skills:



                st.write("**Matched Skills:**")



                skill_html = ""



                for skill in matched_skills:



                    skill_html += (

                        f'<span class="skill-badge">'

                        f'{skill}'

                        f'</span>'

                    )



                st.markdown(

                    skill_html,

                    unsafe_allow_html=True

                )



            else:



                st.write(

                    "**Matched Skills:** None"

                )





            # ==================================

            # VIEW JOB

            # ==================================



            if pd.notna(job["job_url"]):



                st.link_button(

                    "🔗 View Job",

                    job["job_url"]

                )





            st.markdown(

                '</div>',

                unsafe_allow_html=True

            )





    # ======================================

    # CLEAN TEMP FILE

    # ======================================



    os.remove(temp_path)
