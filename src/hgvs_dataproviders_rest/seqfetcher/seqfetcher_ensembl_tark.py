from src.hgvs_dataproviders_rest import HGVSDataNotAvailableError
from src.hgvs_dataproviders_rest.seqfetcher.seqfetcher import SeqFetcher
from src.hgvs_dataproviders_rest.seqfetcher.seqfetcher_fasta import GenomeFastaSeqFetcher, \
    ExonsFromGenomeFastaSeqFetcher
from src.hgvs_dataproviders_rest.seqfetcher.seqfetcher_utils import AbstractTranscriptSeqFetcher, PrefixSeqFetcher, \
    VerifyMultipleSeqFetcher, AlwaysFailSeqFetcher


class _EnsemblTarkTranscriptSeqFetcher(AbstractTranscriptSeqFetcher):
    """ This retrieves sequences from Tark (but not genome/RefSeq checks etc) """
    def _get_transcript_seq(self, ac):
        if ac.startswith("NC_"):
            raise HGVSDataNotAvailableError()

        return self.hdp.get_transcript_sequence(ac)

    @property
    def source(self):
        return f"EnsemblTarkTranscriptSeqFetcher: hdp={self.hdp}"


class EnsemblTarkSeqFetcher(PrefixSeqFetcher):
    _REFSEQ_PREFIXES = {"NM_", "NR_"}

    """ Default for EnsemblTarkDataProvider
        You may need to instantiate your own copy to provide fasta_files """
    def __init__(self, *args, fasta_files=None):
        super().__init__()
        tark_seqfetcher = _EnsemblTarkTranscriptSeqFetcher()
        if fasta_files is not None:
            fasta_seqfetcher = GenomeFastaSeqFetcher(*fasta_files)

            # For RefSeq - Tark doesn't have alignments, so can't check whether there are gaps
            # So we'll look up the genome reference, and if they don't match, throw an error
            class NoValidationExonsFromGenomeFastaSeqFetcher(ExonsFromGenomeFastaSeqFetcher):
                def get_mapping_options(self, ac):
                    # Normal 'get_tx_mapping_options' has a check that causes recursion
                    return self.hdp.get_tx_mapping_options_without_validation(ac)

            exons_seqfetcher = NoValidationExonsFromGenomeFastaSeqFetcher(*fasta_files, cache=True)
            refseq_seqfetcher = VerifyMultipleSeqFetcher(tark_seqfetcher, exons_seqfetcher)
        else:
            fasta_seqfetcher = SeqFetcher()  # Default HGVS
            msg = "You need to provide 'fasta_files' to use RefSeq transcripts. RefSeq transcripts can align with " + \
                   "gaps, so need to compare transcript/genome sequences"
            refseq_seqfetcher = AlwaysFailSeqFetcher(msg)

        self.prefix_seqfetchers.update({
            "NC_": fasta_seqfetcher,
            "ENST": tark_seqfetcher,
        })
        self.prefix_seqfetchers.update({rp: refseq_seqfetcher for rp in self._REFSEQ_PREFIXES})
