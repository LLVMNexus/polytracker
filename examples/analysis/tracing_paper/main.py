from argparse import ArgumentParser
from pathlib import Path
from polytracker import PolyTrackerTrace, TDProgramTrace
from analysis import Analysis
from runner import Runner
from json import load

parser = ArgumentParser(
    prog="compare_tdags",
    description="Compares TDAGs",
)
parser.add_argument(
    "-a",
    "--build_a",
    type=Path,
    help="Path to the first binary build to compare (should be the same software as build b, just built with different options)",
)
parser.add_argument(
    "-ta",
    "--tdag_a",
    type=Path,
    help="Path to the first TDAG (A) trace to compare",
)
parser.add_argument(
    "-fa",
    "--function_id_json_a",
    type=Path,
    help="Path to functionid.json function trace for TDAG A (created by polytracker's cflog pass)",
)
parser.add_argument(
    "-b",
    "--build_b",
    type=Path,
    help="Path to the second binary build to compare (should be the same software as build a, just built with different options)",
)
parser.add_argument(
    "-tb",
    "--tdag_b",
    type=Path,
    help="Path to the second TDAG (B) trace to compare (created by polytracker's cflog pass)",
)
parser.add_argument(
    "-fb",
    "--function_id_json_b",
    type=Path,
    help="Path to functionid.json function trace for TDAG B",
)
parser.add_argument(
    "-e",
    "--execute",
    type=str,
    nargs="+",
    help="command line arguments (including input) to run for each candidate build, for example `<executable_passed_with -a or -b> -i image.j2k -o image.pgm` would require `-i image.j2k -o image.pgm`",
)
parser.add_argument(
    "--cflog",
    action="store_true",
    help="Compare Control Flow Logs (requires -a and -b)",
)
parser.add_argument(
    "--inout",
    action="store_true",
    help="Compare Input-Output mapping (requires -a and -b)",
)
parser.add_argument(
    "--outin",
    action="store_true",
    help="Compare Output-Input mapping (requires -a and -b)",
)
parser.add_argument(
    "--runtrace", action="store_true", help="Compare runtrace (requires -a and -b)"
)
parser.add_argument(
    "--inputsused",
    action="store_true",
    help="Compare inputs used (requires -a and -b)",
)
parser.add_argument(
    "--enumdiff",
    action="store_true",
    help="Enumerate differences (kind of) (requires -a and -b)",
)
parser.add_argument(
    "--cavities",
    help="Contextualize the input trace with blind spots (dont-care bytes)",
    action="store_true",
)
parser.add_argument(
    "--verbose",
    help="Provide the full callstack when comparing cflog traces",
    action="store_true",
)

if __name__ == "__main__":
    comparator = Analysis()
    args = parser.parse_args()

    if args.execute:
        print(f"Running '{args.execute}' for {args.build_a} and {args.build_b}")
        runner = Runner()
        runner.runner(args.build_a, args.build_b, args.execute)
    elif args.tdag_a and args.tdag_b:
        print(f"Comparing {args.tdag_a} and {args.tdag_b}, here we gooooo 🚀")

        traceA: TDProgramTrace = PolyTrackerTrace.load(args.tdag_a)
        traceB: TDProgramTrace = PolyTrackerTrace.load(args.tdag_b)

        if args.cflog and args.function_id_json_a and args.function_id_json_b:
            with open(args.function_id_json_a) as jsonA:
                functions_list_a = load(jsonA)

            with open(args.function_id_json_b) as jsonB:
                functions_list_b = load(jsonB)

            comparator.show_cflog_diff(
                tdagA=traceA.tdfile,
                tdagB=traceB.tdfile,
                functions_list_A=functions_list_a,
                functions_list_B=functions_list_b,
                cavities=args.cavities,
                verbose=args.verbose,
            )

        if args.runtrace:
            comparator.compare_run_trace(traceA.tdfile, traceB.tdfile, args.cavities)

        if args.inputsused:
            comparator.compare_inputs_used(traceA.tdfile, traceB.tdfile)

        if args.enumdiff:
            comparator.enum_diff(traceA.tdfile, traceB.tdfile)
    elif args.tdag_a and args.function_id_json_a and args.cflog:
        print(f"Mapping and showing the control flow log of '{args.tdag_a}'...")
        trace: TDProgramTrace = PolyTrackerTrace.load(args.tdag_a)

        with open(args.function_id_json_a) as function_id_json:
            functions_list = load(function_id_json)

        comparator.show_cflog(
            trace.tdfile, function_id_json, args.cavities, args.verbose
        )
    else:
        print(
            "Error: Need to provide one or two tdags, and corresponding Polytracker-generated function list(s)"
        )
        parser.print_help()
