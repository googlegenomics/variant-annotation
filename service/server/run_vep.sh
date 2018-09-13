
perl $VEP_SCRIPT \
--allele_num \
--check_ref \
--everything \
--vcf_info_field CSQ_VT \
--format vcf \
--tab \
--offline \
--assembly $ASSEMBLY \
-o /dev/stdout \
--force_overwrite \
--no_stats \
--warning_file warnings.txt \
 --dir $VEP_DIR
